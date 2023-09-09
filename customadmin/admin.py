from django.contrib import admin
from django.urls.resolvers import URLResolver
from django.urls import path
from django.http import HttpResponse

# Add custom view to admin site
def some_view(request):
    return HttpResponse('Hello, This is a custom view!')

class CustomAdminSite(admin.AdminSite):
    site_header = 'Info Sharing Forum'
    site_title = 'Info Sharing Forum'
    index_title = 'Info Sharing Forum'

    def get_urls(self) -> list[URLResolver]:
        urls = super().get_urls()

        my_urls = [
            path('my_view/', self.admin_view(some_view))
        ]

        return my_urls + urls

admin_site = CustomAdminSite(name='myadmin')
