from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.utils.translation import gettext_lazy as _

from .forms import PostForm
from .models import Post, HashTag, CustomUser, Follow, PostReaction, Bookmark

from django.views import generic
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def home(request):
    return render(request, 'home.html', {})


class PostCreate(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'create_post.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(PostCreate, self).get_form_kwargs()
        data = self.request.POST.copy()
        hashtags = data.getlist('hashtags')
        hashtags = [hashtag for hashtag in hashtags if hashtag != '']
        if len(hashtags) > 0:
            hashtags = [str(HashTag.objects.get_or_create(name=hashtag)[0].pk) for hashtag in hashtags[0].split(',')]
        data.setlist('hashtags', hashtags)
        kwargs['data'] = data
        return kwargs


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
    search_type = request.GET.get('choices_single_defaul', False)

    if not search_keyword or not search_type:
        return render(request, 'search-post.html', {})

    if search_type == "Post":
        object_list = Post.objects.filter(
            Q(title__icontains=search_keyword) |
            Q(content__icontains=search_keyword)
        )

        for post in object_list:
            reactions = PostReaction.objects.filter(post=post)
            post.feedback_value = sum([reaction.feedback_value for reaction in reactions])

        object_list = sorted(object_list, key=lambda x: x.feedback_value, reverse=True)

    elif search_type == "Author":
        object_list = CustomUser.objects.filter(
            Q(last_name__icontains=search_keyword) |
            Q(first_name__icontains=search_keyword)
        ).order_by('-achievement')

        for user in object_list:
            user.post_count = Post.objects.filter(user=user).count()
            user.follower_count = Follow.objects.filter(followed=user).count()

    paginator = Paginator(object_list, 5)
    page = request.GET.get('page')

    object_list_paginated = get_paginated_object_list(paginator, page)

    context = {
        'object_list': object_list_paginated,
        'choices_single_defaul': search_type,
        'search_keyword': search_keyword,
    }

    return render(request, 'search-post.html', context)


def post_detail_view(request, primary_key):
    post = get_object_or_404(Post, pk=primary_key)
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
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, post=post).exists()
        is_following = Follow.objects.filter(follower=request.user, followed=post.user).exists()
        is_owner = request.user == post.user

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
    })
