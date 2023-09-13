from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import authenticate
from datetime import datetime
from django.utils.translation import gettext_lazy as _

from app.models import CustomUser

class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'username')

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
