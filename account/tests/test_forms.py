from django.test import TestCase
from account.forms import *


class TestForms(TestCase):
    user_params = {
        'first_name': "test",
        'last_name': "test",
        'email': "test@abc.com",
        'username': "taikhoan",
        'password1': "matkhau123",
        'password2': "matkhau123",
    }

    user = None

    @classmethod
    def setUpTestData(cls):
        form = SignUpForm(data=cls.user_params)
        form.save()
        cls.user = CustomUser.objects.get(username=cls.user_params['username'])

    def test_sign_up_form_valid_data(self):
        form = SignUpForm(data={
            'first_name': "test",
            'last_name': "test",
            'email': "gg@gg.com",
            'username': "test",
            'password1': "test123456",
            'password2': "test123456",
        })
        self.assertTrue(form.is_valid())

    def test_sign_up_form_no_data(self):
        form = SignUpForm(data={})
        self.assertFalse(form.is_valid())

    def test_sign_up_form_no_confirm_password(self):
        form = SignUpForm(data={
            'first_name': "test",
            'last_name': "test",
            'email': "gg@gg.com",
            'username': "test",
            'password1': "test123456",
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

    def test_sign_up_form_confirm_password_not_match(self):
        form = SignUpForm(data={
            'first_name': "test",
            'last_name': "test",
            'email': "gg@gg.com",
            'username': "test",
            'password1': "test123456",
            'password2': "test1234567",
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

    def test_sign_up_form_password_too_short(self):
        form = SignUpForm(data={
            'first_name': "test",
            'last_name': "test",
            'email': "gg@gg.com",
            'username': "test",
            'password1': "test",
            'password2': "test",
        })
        self.assertFalse(form.is_valid())

    def test_sign_up_form_username_exist(self):
        form = SignUpForm(data={
            'first_name': "test",
            'last_name': "test",
            'email': "gg@gg.com",
            'username': self.user_params['username'],
            'password1': "test123456",
            'password2': "test123456",
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

    def test_sign_up_form_email_exist(self):
        form = SignUpForm(data={
            'first_name': "test",
            'last_name': "test",
            'email': self.user_params['email'],
            'username': "test",
            'password1': "test123456",
            'password2': "test123456",
        })
        self.assertFalse(form.is_valid())

    def test_sign_in_form_valid_data(self):
        form = SignInForm(data={
            'username': self.user_params['username'],
            'password': self.user_params['password1'],
        })
        self.assertTrue(form.is_valid())

    def test_sign_in_form_no_data(self):
        form = SignInForm(data={})
        self.assertFalse(form.is_valid())

    def test_sign_in_form_username_not_exist(self):
        form = SignInForm(data={
            'username': "test2809",
            'password': 'test123456',
        })
        self.assertFalse(form.is_valid())

    def test_sign_in_form_password_not_match(self):
        form = SignInForm(data={
            'username': self.user_params['username'],
            'password': 'test1234567',
        })
        self.assertFalse(form.is_valid())

    def test_password_reset_form_valid_data(self):
        form = PasswordResetForm(data={
            'email': self.user_params['email'],
        })
        self.assertTrue(form.is_valid())

    def test_password_reset_form_no_data(self):
        form = PasswordResetForm(data={})
        self.assertFalse(form.is_valid())

    def test_password_reset_form_email_not_exist(self):
        form = PasswordResetForm(data={
            'email': "test2809@gg.com",
        })
        self.assertFalse(form.is_valid())

    def test_set_password_form_valid_data(self):
        form = SetPasswordForm(data={
            'new_password1': "test123456",
            'new_password2': "test123456",
        }, user=self.user)
        self.assertTrue(form.is_valid())

    def test_set_password_form_no_data(self):
        form = SetPasswordForm(data={}, user=self.user)
        self.assertFalse(form.is_valid())

    def test_set_password_form_no_confirm_password(self):
        form = SetPasswordForm(data={
            'new_password1': "test123456",
        }, user=self.user)
        self.assertFalse(form.is_valid())

    def test_set_password_form_confirm_password_not_match(self):
        form = SetPasswordForm(data={
            'new_password1': "test123456",
            'new_password2': "test1234567",
        }, user=self.user)
        self.assertFalse(form.is_valid())

    def test_set_password_form_password_too_short(self):
        form = SetPasswordForm(data={
            'new_password1': "test",
            'new_password2': "test",
        }, user=self.user)
        self.assertFalse(form.is_valid())

    def test_set_password_form_password_same_as_old_password(self):
        form = SetPasswordForm(data={
            'new_password1': self.user_params['password1'],
            'new_password2': self.user_params['password1'],
        }, user=self.user)
        self.assertTrue(form.is_valid())
