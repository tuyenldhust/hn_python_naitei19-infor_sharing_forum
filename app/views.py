from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import PostForm
from .models import Post, HashTag

from app.models import Post, PostReaction, CustomUser, Follow
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
