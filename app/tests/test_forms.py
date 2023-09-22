from django.test import TestCase
from app.forms import *
from app.models import *


class TestForms(TestCase):
    categories = []
    hashtags = []

    @classmethod
    def setUpTestData(cls):
        cls.categories = [Category.objects.create(name="category" + str(i)) for i in range(5)]
        cls.hashtags = [HashTag.objects.create(name="hashtag" + str(i)) for i in range(5)]

    def test_post_form_valid_data(self):
        form = PostForm(data={
            'title': "test",
            'categories': [self.categories[0]],
            'content': "test",
            'hashtags': [self.hashtags[0]],
            'mode': 0,
            'status': 0,
        })
        self.assertTrue(form.is_valid())

    def test_post_form_no_data(self):
        form = PostForm(data={})
        self.assertFalse(form.is_valid())

    def test_post_form_invalid_title(self):
        form = PostForm(data={
            'title': None,
            'categories': [self.categories[0]],
            'content': "test",
            'hashtags': [self.hashtags[0]],
            'mode': 0,
            'status': 0,
        })
        self.assertFalse(form.is_valid())

    def test_post_form_invalid_content(self):
        form = PostForm(data={
            'title': "test",
            'categories': [self.categories[0]],
            'content': None,
            'hashtags': [self.hashtags[0]],
            'mode': 0,
            'status': 0,
        })
        self.assertFalse(form.is_valid())

    def test_post_form_invalid_mode(self):
        form = PostForm(data={
            'title': "test",
            'categories': [self.categories[0]],
            'content': "test",
            'hashtags': [self.hashtags[0]],
            'mode': 2,
            'status': 0,
        })
        self.assertFalse(form.is_valid())

    def test_post_form_invalid_status(self):
        form = PostForm(data={
            'title': "test",
            'categories': [self.categories[0]],
            'content': "test",
            'hashtags': [self.hashtags[0]],
            'mode': 0,
            'status': 6,
        })
        self.assertFalse(form.is_valid())

    def test_post_form_invalid_category(self):
        form = PostForm(data={
            'title': "test",
            'categories': 'abc',
            'content': "test",
            'hashtags': [self.hashtags[0]],
            'mode': 0,
            'status': 0,
        })
        self.assertFalse(form.is_valid())

    def test_post_form_removed_category(self):
        removed_category = self.categories[0]
        removed_category.delete()
        form = PostForm(data={
            'title': "test",
            'categories': [removed_category],
            'content': "test",
            'hashtags': [self.hashtags[0]],
            'mode': 0,
            'status': 0,
        })
        self.assertFalse(form.is_valid())

    def test_post_form_invalid_hashtag(self):
        form = PostForm(data={
            'title': "test",
            'categories': [self.categories[0]],
            'content': "test",
            'hashtags': 'abc',
            'mode': 0,
            'status': 0,
        })
        self.assertFalse(form.is_valid())
