from django.shortcuts import render
from .forms import SignUpForm, SignInForm
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
import re

from .tokens import account_activation_token

# clean all html tags in message
def clean_message(text):
    return re.sub('<[^<]+?>', '', str(text))

def activateEmail(request, user, to_email):
    mail_subject = 'Kích hoạt tài khoản'
    message = render_to_string('account/activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Chúng tôi đã gửi link kích hoạt tài khoản cho bạn thông qua email.')
    else:
        messages.error(request, f'Đã có lỗi xảy ra trong quá trình gửi mail. Vui lòng thử lại sau.')

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Kích hoạt tài khoản thành công!')
        return redirect('signin')
    else:
        messages.error(request, 'Link kích hoạt tài khoản không hợp lệ!')
    
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            messages.success(request, _('Đăng ký thành công!'))
            activateEmail(request, user, request.POST['email'])
            return redirect('home')
        else:
            for error in list(form.errors.values()):
                messages.error(request, clean_message(error))
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

def signout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, _('Đăng xuất thành công!'))
    else:
        messages.info(request, _('Bạn chưa đăng nhập!'))
    return redirect('home')
