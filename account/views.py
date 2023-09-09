from django.shortcuts import render
from .forms import SignUpForm
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
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
            for error in list(form.errors.values()):
                messages.error(request, clean_message(error))
    else:
        form = SignUpForm()
    return render(request, 'account/signup.html', {'form': form})
