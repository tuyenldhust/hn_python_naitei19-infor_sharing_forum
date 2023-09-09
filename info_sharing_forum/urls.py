"""
URL configuration for info_sharing_forum project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from customadmin.admin import admin_site

admin_site._registry.update(admin.site._registry)

urlpatterns = [
    re_path(r'admin/', admin_site.urls),
    path('account/', include('account.urls')),
    path('', include('app.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
