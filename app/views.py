import json

from django.db import transaction, IntegrityError
from django.db.models import Sum
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from .forms import PostForm
from .models import Post, HashTag, CustomUser, Follow, PostReaction, Bookmark, Comment, Category

from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def __get_trending_post_by_time(time, limit=5):
    return Post.objects.raw(
        "select p.*, count(distinct r.id) as r_count, "
        "group_concat(distinct c.name separator ', ') as list_categories "
        'from app_post p '
        'join app_postreaction r on p.id = r.post_id '
        'join app_post_categories pc on p.id = pc.post_id '
        'join app_category c on c.id = pc.category_id '
        'where r.feedback_value = 1 '
        '  and p.status = 1'
        '  and r.time > (now() - interval %s day) '
        'group by p.id '
        'order by r_count desc '
        'limit %s', [time, limit])


def __get_trending(limit=5):
    return [
        {
            'title': _('Bài viết nổi bật trong tuần'),
            'posts': __get_trending_post_by_time(7, limit)
        },
        {
            'title': _('Bài viết nổi bật trong tháng'),
            'posts': __get_trending_post_by_time(30, limit)
        },
        {
            'title': _('Bài viết nổi bật trong năm'),
            'posts': __get_trending_post_by_time(365, limit)
        }

    ]


def home(request):
    return render(request, 'home.html', {
        'all_top_posts': __get_trending(),
    })


class PostCreate(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'create_post.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    @transaction.atomic
    def get_form_kwargs(self):
        try:
            with transaction.atomic():
                kwargs = super(PostCreate, self).get_form_kwargs()
                data = self.request.POST.copy()
                if data.get('status') is None:
                    data['status'] = 1
                if data.get('mode') == '1':
                    data['status'] = 4
                hashtags = data.getlist('hashtags')
                hashtags = [hashtag for hashtag in hashtags if hashtag != '']
                if len(hashtags) > 0:
                    hashtags = [str(HashTag.objects.get_or_create(name=hashtag)[0].pk) for hashtag in
                                hashtags[0].split(',')]
                data.setlist('hashtags', hashtags)
                kwargs['data'] = data
                return kwargs
        except IntegrityError:
            return HttpResponseBadRequest()

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'primary_key': self.object.pk})


def get_paginated_object_list(paginator, page):
    try:
        object_list_paginated = paginator.page(page)
    except PageNotAnInteger:
        object_list_paginated = paginator.page(1)
    except EmptyPage:
        object_list_paginated = paginator.page(paginator.num_pages)

    return object_list_paginated


def homepageSearch(request):
    # object_list = Post.objects.all()
    search_keyword = request.GET.get('search_keyword', False)
    search_type = request.GET.get('choices_single_default', False)

    if not search_keyword or not search_type:
        return render(request, 'search.html', {})

    if search_type == "Post":
        object_list = Post.objects.filter(
            Q(title__icontains=search_keyword) |
            Q(content__icontains=search_keyword),
            status=1
        )

        for post in object_list:
            reactions = PostReaction.objects.filter(post=post)
            post.feedback_value = sum([reaction.feedback_value for reaction in reactions])
            # count bookmark
            post.bookmark_count = Bookmark.objects.filter(post=post).count()
            # count comment
            post.comment_count = Comment.objects.filter(post=post).count()

        object_list = sorted(object_list, key=lambda x: x.feedback_value, reverse=True)

    elif search_type == "Author":
        object_list = CustomUser.objects.filter(
            Q(last_name__icontains=search_keyword) |
            Q(first_name__icontains=search_keyword)
        ).order_by('-achievement')

        for user in object_list:
            user.post_count = Post.objects.filter(user=user).count()
            user.follower_count = Follow.objects.filter(followed=user).count()

    paginator = Paginator(object_list, 9)
    page = request.GET.get('page')

    object_list_paginated = get_paginated_object_list(paginator, page)

    context = {
        'object_list': object_list_paginated,
        'choices_single_default': search_type,
        'search_keyword': search_keyword,
    }

    return render(request, 'search.html', context)


def get_message_404(status):
    if status == 0:
        return _('Post is not existed.')
    elif status == 2:
        return _('Post is deleted.')
    elif status == 3:
        return _('Post is banned.')
    elif status == 4:
        return _('Post is waiting for approval.')
    elif status == 5:
        return _('Post is rejected.')


def post_detail_view(request, primary_key):
    post = get_object_or_404(Post, pk=primary_key)
    notice_type = (
        (0, _('Draft')),
        (1, None),
        (2, _('Deleted')),
        (3, _('Banned')),
        (4, _('Pending')),
        (5, _('Rejected')),
    )
    if post.status != 1 and not request.user.is_superuser:
        if post.status in [2, 3, 5] or (post.status in [0, 4] and post.user != request.user):
            return render(request, '404.html', {'message': get_message_404(post.status)})
    feedback_value = PostReaction.objects.filter(post=post).aggregate(Sum('feedback_value'))['feedback_value__sum']
    if feedback_value is None:
        feedback_value = 0

    achievement_rank = [_('Unranked'), _('Bronze'), _('Silver'), _('Gold'), _('Platinum'), _('Diamond')][
        post.user.achievement]
    achievement_color = ['#242132', 'brown', 'grey', '#f6ca15', 'lightblue', '#e5b9f4'][post.user.achievement]

    view_count = post.view_count
    post.view_count = view_count + 1
    post.save()

    is_bookmarked = False
    is_following = False
    is_owner = False
    reacted_value = None
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, post=post).exists()
        is_following = Follow.objects.filter(follower=request.user, followed=post.user).exists()
        is_owner = request.user == post.user
        reacted = PostReaction.objects.filter(user=request.user, post=post).first()
        if reacted is not None:
            reacted_value = reacted.feedback_value

    # Load comments
    comments = Comment.objects.filter(post=post).order_by('-updated_at')
    comments_tree = {comment for comment in comments if comment.parent.pk == -1}

    for comment in comments_tree:
        comment.child = {child for child in comments if child.parent.pk == comment.pk}

    return render(request, 'post_detail.html', context={
        'post': post,
        'author': post.user,
        'achievement_rank': achievement_rank,
        'achievement_color': achievement_color,
        'view_count': view_count.as_integer_ratio()[0],
        'followers_count': Follow.objects.filter(followed=post.user).count(),
        'feedback_value': feedback_value,
        'categories': post.categories.all(),
        'hashtags': post.hashtags.all(),
        'is_bookmarked': is_bookmarked,
        'is_following': is_following,
        'is_owner': is_owner,
        'comments_tree': comments_tree,
        'reacted_value': reacted_value,
        'notice': notice_type[post.status][1],
    })


@transaction.atomic
def edit_post_view(request, primary_key):
    try:
        with transaction.atomic():
            post = get_object_or_404(Post, pk=primary_key, user=request.user)
            if request.method == 'POST':
                data = request.POST.copy()
                if data.get('status') is None:
                    data['status'] = 1
                if data.get('mode') == '1':
                    data['status'] = 4
                hashtags = data.getlist('hashtags')
                hashtags = [hashtag for hashtag in hashtags if hashtag != '']
                if len(hashtags) > 0:
                    hashtags = [str(HashTag.objects.get_or_create(name=hashtag)[0].pk) for hashtag in
                                hashtags[0].split(',')]
                data.setlist('hashtags', hashtags)
                request.POST = data
                form = PostForm(request.POST, instance=post)
                if form.is_valid():
                    form.save()
                    post.categories.clear()
                    post.hashtags.clear()
                    for category in form.cleaned_data['categories']:
                        post.categories.add(category)
                    for hashtag in form.cleaned_data['hashtags']:
                        post.hashtags.add(hashtag)
                    return redirect('post_detail', primary_key=post.pk)
            else:
                form = PostForm(instance=post)
            hashtags = [hashtag.name for hashtag in post.hashtags.all()]
            hashtags = ','.join(hashtags)
            return render(request, 'edit_post.html', {
                'form': form,
                'id': post.pk,
                'hashtags': hashtags,
                'content': post.content,
            })
    except IntegrityError:
        return HttpResponseBadRequest()


def delete_post_view(request, primary_key):
    post = get_object_or_404(Post, pk=primary_key, user=request.user)
    post.status = 2
    post.save()
    return redirect('home')


def comment(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        content = request.POST.get('comment_content')

        if content is None or content == '':
            messages.error(request, _('Nội dung bình luận không được để trống!'))
            return redirect('post_detail', primary_key=post_id)

        parent_id = request.POST.get('parent_id')

        post = get_object_or_404(Post, pk=post_id)

        parent = get_object_or_404(Comment, pk=parent_id)

        comment = Comment.objects.create(user=request.user, post=post, parent=parent, content=content, is_edited=False)

    return redirect('post_detail', primary_key=post_id)


@csrf_exempt
def react_post_view(request, primary_key, react_type):
    if request.method == 'POST' and request.user.is_authenticated and react_type in ['upvote', 'downvote']:
        value = ({
            'upvote': 1,
            'downvote': -1,
        })
        feedback_value = value.get(react_type)
        post = get_object_or_404(Post, pk=primary_key)
        reaction = PostReaction.objects.filter(post=post, user=request.user)
        if reaction.exists():
            if reaction.first().feedback_value == feedback_value:
                reaction.delete()
                message = 'deleted'
            else:
                reaction = reaction.first()
                reaction.feedback_value = feedback_value
                message = react_type
                reaction.save()
        else:
            reaction = PostReaction.objects.create(post=post, user=request.user, feedback_value=feedback_value)
            message = react_type
            reaction.save()
        total_feedback_value = PostReaction.objects.filter(post=post).aggregate(Sum('feedback_value'))[
            'feedback_value__sum']
        if total_feedback_value is None:
            total_feedback_value = 0
        return HttpResponse(json.dumps({
            'message': message,
            'total_feedback_value': total_feedback_value,
        }), content_type='application/json')
    else:
        return HttpResponseBadRequest(
            json.dumps({
                'message': 'Bad Request',
            }), content_type='application/json')


@csrf_exempt
def bookmark_post_view(request, primary_key):
    if request.method == 'POST' and request.user.is_authenticated:
        post = get_object_or_404(Post, pk=primary_key)
        bookmark = Bookmark.objects.filter(post=post, user=request.user)
        if bookmark.exists():
            bookmark.delete()
            message = 'deleted'
        else:
            bookmark = Bookmark.objects.create(post=post, user=request.user)
            message = 'bookmarked'
            bookmark.save()
        return HttpResponse(json.dumps({
            'message': message,
        }), content_type='application/json')
    else:
        return HttpResponseBadRequest(
            json.dumps({
                'message': 'Bad Request',
            }), content_type='application/json')


def trending_posts_view(request):
    return render(request, 'trending.html', {
        'all_top_posts': __get_trending(20)
    })
