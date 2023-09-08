from django.shortcuts import render
from .forms import SignUpForm, LoginForm
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate, logout

def index(request):
    return render(request, 'account/index.html')

def signin(request):
    error = False
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username = request.POST['username'], password = request.POST['password'])
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                error = True
    else:
        form = LoginForm()
    return render(request, 'account/signin.html', {'form': form, 'error': error})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'account/signup.html', {'form': form})

def signout(request):
    logout(request)
    return redirect('index')
