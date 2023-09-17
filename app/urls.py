from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('create-post', login_required(views.PostCreate.as_view(), login_url='/account/signin/'), name="create_post"),
    path('homepage-search-bar/', views.homepageSearch, name="homepage-search-bar"),
    path('post/<int:primary_key>', views.post_detail_view, name="post_detail"),
    path('post/<int:primary_key>/edit', views.edit_post_view, name="edit_post"),
    path('post/<int:primary_key>/delete', views.delete_post_view, name="delete_post"),
    path('comment/', views.comment, name="comment"),
]
