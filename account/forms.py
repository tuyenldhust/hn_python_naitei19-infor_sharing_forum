from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django import forms
from django.contrib.auth import authenticate
from datetime import datetime
from django.utils.translation import gettext_lazy as _

from app.models import CustomUser

class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'username')

    def clean(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Email đã tồn tại!"))
        return self.cleaned_data

class SignInForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=30, widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        if user is None:
            raise forms.ValidationError(_("Tài khoản không tồn tại hoặc sai tên đăng nhập hoặc sai mật khẩu!"))
        else:
            if not user.is_active and user.count_violated < 3:
                raise forms.ValidationError(_("Tài khoản của bạn chưa được kích hoạt, vui lòng kiểm tra email!"))
            elif not user.is_active and user.count_violated >= 3:
                raise forms.ValidationError(_("Tài khoản của bạn đã bị cấm vĩnh viễn!"))
            elif user.is_active and user.count_violated < 3 and user.time_banned is not None and (datetime.now().date() - user.time_banned.date()).days < 14:
                raise forms.ValidationError(_("Tài khoản của bạn đã bị khóa trong 14 ngày!"))

        return self.cleaned_data

class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Email không tồn tại!"))
        return self.cleaned_data


class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = CustomUser
        fields = ['new_password1', 'new_password2']
