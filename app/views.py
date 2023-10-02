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

from .forms import PostForm, FilterForm
from .models import Post, HashTag, CustomUser, Follow, PostReaction, Bookmark, Comment, Category, PostPaid, Notification

from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from datetime import datetime
from django.contrib.auth.decorators import login_required


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


def __get_famous_author_by_time(time, limit=5):
    list_author = CustomUser.objects.raw(
        'select c.username, c.id, c.achievement, '
        '       concat(c.last_name, \' \', c.first_name) as full_name, '
        '       c.avatar_link, '
        '       count(distinct r.user_id)              as liked_people '
        'from app_post p '
        '         join app_postreaction r on p.id = r.post_id '
        '         join app_customuser c on c.id = p.user_id '
        'where r.feedback_value = 1 '
        '  and p.status = 1 '
        '  and r.time > (now() - interval %s day) '
        'group by c.username '
        'order by liked_people desc '
        'limit %s', [time, limit])

    for author in list_author:
        author.achievement_rank, author.achievement_color = __get_color_rank(int(author.achievement))
    return list_author


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


def __get_famous_author(limit=5):
    return [
        {
            'title': _('Tác giả nổi bật trong tuần'),
            'authors': __get_famous_author_by_time(7, limit)
        },
        {
            'title': _('Tác giả nổi bật trong tháng'),
            'authors': __get_famous_author_by_time(30, limit)
        },
        {
            'title': _('Tác giả nổi bật trong năm'),
            'authors': __get_famous_author_by_time(365, limit)
        }

    ]


def home(request):
    new_posts = Post.objects.filter(status=1).order_by('-created_at')[:10]
    return render(request, 'home.html', {
        'all_top_posts': __get_trending(),
        'all_top_authors': __get_famous_author(),
        'new_posts': new_posts
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
    params = request.GET
    search_keyword = params.get('search_keyword', False)
    search_type = params.get('choices_single_default', False)

    # Get value from search filter (if exist)
    search_category_list = params.getlist('list_category', False)
    from_date = params.get('from_date', False)
    to_date = params.get('to_date', False)
    point = params.get('point', False)

    # Process "False" str from pagination link
    if type(search_category_list) == list:
        if "False" in search_category_list:
            search_category_list = False
    if from_date == "False":
        from_date = False
    if to_date == "False":
        to_date = False
    if point == "False":
        point = False

    if not search_keyword or not search_type:
        return render(request, 'search.html', {})

    if search_type == "Post":
        query = Q(title__icontains=search_keyword) | Q(content__icontains=search_keyword)

        # Filter by date
        if from_date:
            from_date_query = datetime.strptime(from_date, '%m/%d/%Y').strftime('%Y-%m-%d')
            query &= Q(created_at__gte=from_date_query)
        if to_date:
            to_date_query = datetime.strptime(to_date, '%m/%d/%Y').strftime('%Y-%m-%d')
            query &= Q(created_at__lte=to_date_query)

        object_list = Post.objects.filter(query, status=1)

        # Filter by category
        if search_category_list:
            # If search_category_list is from pagination link
            # If [ character is in search_category_list[0], it means that search_category_list is from pagination link
            if "[" in search_category_list[0]:
                search_category_list = eval(search_category_list[0])
            for category in search_category_list:
                object_list = object_list.filter(categories__pk=category)

        for post in object_list:
            reactions = PostReaction.objects.filter(post=post)
            post.feedback_value = sum([reaction.feedback_value for reaction in reactions])
            # count bookmark
            post.bookmark_count = Bookmark.objects.filter(post=post).count()
            # count comment
            post.comment_count = Comment.objects.filter(post=post).count()

        # Filter by point (feedback_value)
        if point:
            if point == '----':
                pass
            elif point == '<100':
                object_list = [post for post in object_list if post.feedback_value < 100]
            elif point == '100-499':
                object_list = [post for post in object_list if 100 <= post.feedback_value <= 499]
            elif point == '500-999':
                object_list = [post for post in object_list if 500 <= post.feedback_value <= 999]
            elif point == '>1000':
                object_list = [post for post in object_list if post.feedback_value > 1000]

        # Short by feedback_value
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

    # Render filter form if exist
    if search_category_list or from_date or to_date or point:
        filter_form = FilterForm(initial={
            'list_category': search_category_list,
            'from_date': from_date,
            'to_date': to_date,
            'point': point,
        })
    else:
        filter_form = FilterForm()

    object_list_paginated = get_paginated_object_list(paginator, page)

    context = {
        'object_list': object_list_paginated,
        'choices_single_default': search_type,
        'search_keyword': search_keyword,
        'filter_form': filter_form,
        'list_category': search_category_list,
        'from_date': from_date,
        'to_date': to_date,
        'point': point,
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


def __get_color_rank(achievement):
    achievement_rank = [_('Unranked'), _('Bronze'), _('Silver'), _('Gold'), _('Platinum'), _('Diamond')][achievement]
    achievement_color = ['#242132', 'brown', 'grey', '#f6ca15', 'lightblue', '#e5b9f4'][achievement]
    return achievement_rank, achievement_color


def __substring_content_safe(content):
    temp = content[:min(1000, int(len(content) * 0.1))]
    last_open_ab = temp.rfind('<')
    last_close_ab = temp.rfind('>')
    if last_open_ab > last_close_ab:
        temp = content[:last_close_ab + 1 + content.find('>', last_open_ab)]
    return temp + '...'


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

    achievement_rank, achievement_color = __get_color_rank(int(post.user.achievement))

    if request.session.get('viewed_post_' + str(post.pk)) is None:
        request.session['viewed_post_' + str(post.pk)] = True
        post.view_count = post.view_count + 1
        post.save()
    view_count = post.view_count

    is_bookmarked = False
    is_following = False
    is_owner = False
    reacted_value = None
    is_paid = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, post=post).exists()
        is_following = Follow.objects.filter(follower=request.user, followed=post.user).exists()
        is_owner = request.user == post.user
        reacted = PostReaction.objects.filter(user=request.user, post=post).first()
        is_paid = PostPaid.objects.filter(user=request.user, post=post).exists()
        if reacted is not None:
            reacted_value = reacted.feedback_value

    # limit content length 10% of total characters(max 1000 characters)
    if post.mode == 1 and not is_owner and not request.user.is_staff and not is_paid:
        post.content = __substring_content_safe(post.content)
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
        'is_paid': is_paid,
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

        if request.user.username != post.user.username:
            if parent_id == '-1':
                notification = Notification.objects.create(
                    action_user=request.user,
                    receive_user=post.user,
                    type_notify=1,
                    content=post.id
                )
            else:
                # search user who comment parent comment
                parent_comment = Comment.objects.get(pk=parent_id)
                if parent_comment is not None and parent_comment.user != request.user:
                    notification = Notification.objects.create(
                        action_user=request.user,
                        receive_user=parent_comment.user,
                        type_notify=2,
                        content=post.id
                    )

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

                # delete notification if user remove react type
                _delete_notify(request.user, post.user, post.id)
            else:
                reaction = reaction.first()
                reaction.feedback_value = feedback_value
                message = react_type
                reaction.save()

                # delete notification if user change react type to downvote
                _delete_notify(request.user, post.user, post.id)
        else:
            reaction = PostReaction.objects.create(post=post, user=request.user, feedback_value=feedback_value)
            message = react_type
            reaction.save()

            # create notification
            if react_type == 'upvote':
                if request.user != post.user:
                    notification = Notification.objects.create(
                        action_user=request.user,
                        receive_user=post.user,
                        type_notify=0,
                        content=post.id
                    )

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

def _delete_notify(action_user, receive_user, post_id, type_notify=0):
    notifications = Notification.objects.filter(action_user=action_user, receive_user=receive_user, content=post_id, type_notify=type_notify)
    if notifications.exists():
        notifications.delete()

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


def famous_authors_view(request):
    return render(request, 'famous_author.html', {
        'all_top_authors': __get_famous_author(20)
    })


@csrf_exempt
def pay_post_view(request, primary_key):
    try:
        with transaction.atomic():
            if request.method == 'POST' and request.user.is_authenticated:
                post = get_object_or_404(Post, pk=primary_key)
                if PostPaid.objects.filter(post=post, user=request.user).exists():
                    return HttpResponseBadRequest(
                        json.dumps({
                            'message': 'Bài viết đã được thanh toán'
                        }), content_type='application/json')
                if request.user.point < 10:
                    return HttpResponseBadRequest(
                        json.dumps({
                            'message': 'Không đủ điểm để thanh toán'
                        }), content_type='application/json')
                else:
                    request.user.point -= 10
                    request.user.save()
                    post.user.point += 5
                    post.user.save()
                    postpaid = PostPaid.objects.create(post=post, user=request.user)
                    postpaid.save()
                    return HttpResponse(json.dumps({
                        'message': 'Thanh toán thành công'
                    }), content_type='application/json')
    finally:
        return HttpResponseBadRequest(
            json.dumps({
                'message': 'Có lỗi xảy ra'
            }), content_type='application/json')


@csrf_exempt
def follow_user_view(request, primary_key):
    if request.method == 'POST' and request.user.is_authenticated:
        user = get_object_or_404(CustomUser, pk=primary_key)
        follow = Follow.objects.filter(follower=request.user, followed=user)
        if follow.exists():
            follow.delete()
            return HttpResponse(json.dumps({
                'type': 'unfollowed',
                'followers_count': Follow.objects.filter(followed=user).count(),
                'message': 'Bỏ theo dõi thành công'
            }), content_type='application/json')
        else:
            Follow.objects.create(follower=request.user, followed=user)
            return HttpResponse(json.dumps({
                'type': 'followed',
                'followers_count': Follow.objects.filter(followed=user).count(),
                'message': 'Theo dõi thành công'
            }), content_type='application/json')
    else:
        return HttpResponseBadRequest(
            json.dumps({
                'message': 'Có lỗi xảy ra'
            }), content_type='application/json')

@login_required(login_url='/account/signin/')
@csrf_exempt
def read_all_notify_view(request):
    if request.method == 'POST' and request.user.is_authenticated:
        notifications = Notification.objects.filter(receive_user=request.user, is_read=False)
        for notification in notifications:
            notification.is_read = True
            notification.save()
        return HttpResponse(json.dumps({
            'message': _('Đã đọc tất cả thông báo')
        }), content_type='application/json')
    else:
        return HttpResponseBadRequest(
            json.dumps({
                'message': _('Có lỗi xảy ra')
            }), content_type='application/json')


def all_posts_view(request):
    all_posts = Post.objects.filter(status=1)
    return render(request, 'all_post.html', {
        'object_list': Paginator(all_posts, 10).get_page(request.GET.get('page')),
    })
