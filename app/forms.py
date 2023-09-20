from ckeditor import widgets
from django import forms
from django.shortcuts import get_object_or_404

from app.models import Post, Category
from django.utils.translation import gettext_lazy as _


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
