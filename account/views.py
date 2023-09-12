from django.shortcuts import render
from .forms import SignUpForm, SignInForm
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
import re

# clean all html tags in message
def clean_message(text):
    return re.sub('<[^<]+?>', '', str(text))

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            return redirect('home')
        else:
            form = SignUpForm()
        return render(request, 'account/signup.html', {'form': form})
        
def signin(request):
    if request.user.is_authenticated:
        messages.info(request, _('Bạn đã đăng nhập rồi!'))
        return redirect('home')
    
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            user = authenticate(username = request.POST['username'], password = request.POST['password'])
            if user is not None:
                login(request, user)
                messages.success(request, _('Đăng nhập thành công!'))
                return redirect('home')
        else:
            for error in list(form.errors.values()):
                messages.error(request, clean_message(error))
    else:
        form = SignInForm()
    return render(request, 'account/signin.html', {'form': form})
