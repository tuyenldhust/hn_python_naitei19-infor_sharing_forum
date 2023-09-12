from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import authenticate

from app.models import CustomUser

class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'username')
