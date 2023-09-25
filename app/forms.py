from ckeditor import widgets
from django import forms
from django.shortcuts import get_object_or_404

from app.models import Post, Category, CustomUser
from django.utils.translation import gettext_lazy as _
import re


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'categories', 'content', 'hashtags', 'mode', 'status')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title (*)'}),
            'categories': forms.SelectMultiple(),
            'content': forms.CharField(widget=widgets.CKEditorWidget()),
            'mode': forms.Select(attrs={'class': 'btn btn-default border border-gray'}),
        }
        # not required hashtags field
        required = {'hashtags': False}

    def clean(self):
        cleaned_data = super(PostForm, self).clean()
        title = cleaned_data.get('title')
        content = cleaned_data.get('content')
        categories = cleaned_data.get('categories')
        mode = cleaned_data.get('mode')
        status = cleaned_data.get('status')
        if not title and not content and not categories and not mode and not status:
            raise forms.ValidationError(_('You have to complete all fields!'))
        if not isinstance(title, str):
            raise forms.ValidationError(_('Title must be string!'))
        if not isinstance(content, str):
            raise forms.ValidationError(_('Content must be string!'))
        if len(title) == 0:
            raise forms.ValidationError(_('Title must be at least 1 character!'))
        if len(content) == 0:
            raise forms.ValidationError(_('Content must be at least 1 character!'))
        if mode not in [0, 1]:
            raise forms.ValidationError(_('You have to choose valid mode!'))
        if status not in [0, 1, 2, 3, 4, 5]:
            raise forms.ValidationError(_('You have to choose valid status!'))
        try:
            [get_object_or_404(Category, pk=category.pk) for category in categories]
        except:
            raise forms.ValidationError(_('You have to choose valid categories!'))
        return cleaned_data
    
class CustomCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

    def clean_name(self):
        name = self.cleaned_data['name']

        # Check if name is already exist and lowercase
        if Category.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError(_('Tên danh mục đã tồn tại'))
        return name

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

    def clean_username(self):
        username = self.cleaned_data['username']

        # Check if username is already exist and lowercase
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_('Tên tài khoản đã tồn tại'))
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']

        # Check email with regex
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise forms.ValidationError(_('Email không hợp lệ'))
        # Check if email is already exist and lowercase
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('Email đã tồn tại'))
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data['phone']

        # Check phone with regex
        if not re.match(r"^[0-9]{10}$", phone):
            raise forms.ValidationError(_('Số điện thoại không hợp lệ'))
        # Check if phone is already exist and lowercase
        if CustomUser.objects.filter(phone__iexact=phone).exists():
            raise forms.ValidationError(_('Số điện thoại đã tồn tại'))
        return phone
    
    def clean_point(self):
        point = self.cleaned_data['point']
        if point < 0:
            raise forms.ValidationError(_('Điểm không hợp lệ'))
        return point
    
    def clean_achievement(self):
        achievement = self.cleaned_data['achievement']
        if achievement < 0:
            raise forms.ValidationError(_('Thành tích không hợp lệ'))
        return achievement
    
    def clean_count_violated(self):
        count_violated = self.cleaned_data['count_violated']
        if count_violated == None:
            count_violated = 0
        if count_violated < 0 or count_violated > 3:
            raise forms.ValidationError(_('Số lần vi phạm không hợp lệ'))
        return count_violated
    
    def clean_avatar_link(self):
        avatar_link = self.cleaned_data['avatar_link']
        if avatar_link == None:
            avatar_link = '/static/user_layout/images/default-avatar.jpg'
        return avatar_link

    # Save with hash password
    def save(self, commit=True):
        user = super(CustomUserForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
