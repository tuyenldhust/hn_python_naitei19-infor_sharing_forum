from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('reset/<uidb64>/<token>', views.passwordResetConfirm, name='password_reset_confirm'),
    path('<str:username>', views.show_profile, name='profile'),
    path('<str:username>/edit', views.edit_profile, name='edit_profile'),
    path('<str:username>/change_password', views.change_password, name='change_password'),
    path('<str:username>/voted_up', views.voted_up, name='voted_up'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
