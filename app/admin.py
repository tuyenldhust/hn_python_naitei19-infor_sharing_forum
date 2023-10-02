from typing import Any
from django.contrib import admin
from django.db.models.expressions import OrderBy, RawSQL
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.db.models import Value
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _
from app.models import Category, CustomUser, Post
from app.forms import CustomCategoryForm, CustomUserForm

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CustomCategoryForm
    list_display = ('id', 'name')
    search_fields = ['name']
    list_per_page = 10

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserForm
    list_display = ('id', 'username', 'full_name', 'email', 'achievement', 'point', 'phone', 'last_login', 'date_joined', 'is_superuser', 'is_staff', 'is_active', 'count_violated', 'time_banned', 'is_deleted')
    list_editable = ('achievement', 'point', 'last_login', 'date_joined', 'is_superuser', 'is_staff', 'is_active', 'count_violated', 'time_banned', 'is_deleted')
    search_fields = ['username', 'full_name', 'email']
    list_per_page = 20

    @admin.display(description='Họ tên', ordering=OrderBy(
        RawSQL(
            "CONCAT(first_name, ' ', last_name)",
            tuple()
        )
    ))
    def full_name(self, obj):
        return obj.get_full_name()
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)
        qs = qs.annotate(
            full_name=Concat(
                "first_name",
                Value("_"),
                "last_name"
            )
        )
        return qs
