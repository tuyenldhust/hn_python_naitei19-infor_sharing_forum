from django.urls import path
from . import views_api

urlpatterns = [
    path('upload_avatar', views_api.upload_avatar, name='upload_avatar'),
]
