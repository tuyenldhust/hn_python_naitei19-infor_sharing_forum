from django.shortcuts import render
from .forms import SignUpForm, SignInForm, PasswordResetForm, SetPasswordForm
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.db.models.query_utils import Q
import re

from .tokens import account_activation_token

def index(request):
    return render(request, 'account/index.html')

# clean all html tags in message
def clean_message(text):
    return re.sub('<[^<]+?>', '', str(text))

def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('account/activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Đăng kí thành công. Hãy kiểm tra email để kích hoạt tài khoản.')
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
    
    return redirect('index')

def signin(request):
    if request.user.is_authenticated:
        messages.info(request, 'Bạn đã đăng nhập rồi!')
        return redirect('index')
    
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            user = authenticate(username = request.POST['username'], password = request.POST['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'Đăng nhập thành công!')
                return redirect('index')
        else:
            for error in list(form.errors.values()):
                messages.error(request, clean_message(error))
    else:
        form = SignInForm()
    return render(request, 'account/signin.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('index')
        else:
            for error in list(form.errors.values()):
                messages.error(request, clean_message(error))
    else:
        form = SignUpForm()
    return render(request, 'account/signup.html', {'form': form})

def signout(request):
    logout(request)
    messages.success(request, 'Đăng xuất thành công!')
    return redirect('index')

def password_reset_request(request):
    if request.user.is_authenticated:
        messages.warning(request, 'Bạn đang đăng nhập!!!')
        return redirect('index')
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Đặt lại mật khẩu"
                message = render_to_string("account/template_reset_password.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                    messages.success(request, "Chúng tôi đã gửi email để reset mật khẩu của bạn")
                else:
                    messages.error(request, "Đã có lỗi xảy ra trong quá trình gửi mail. Vui lòng thử lại sau.")
                return redirect("index")
            else:
                messages.error(request, "Không có tài khoản nào được liên kết với email này")
        else:
            for error in list(form.errors.values()):
                messages.error(request, clean_message(error))
    else:
        form = PasswordResetForm()
    
    return render(request=request, template_name="account/password_reset.html", context={"form":form})

def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Đặt lại mật khẩu thành công. Bạn có thể đăng nhập bằng mật khẩu mới.")
                return redirect('signin')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, clean_message(error))
        else:
            form = SetPasswordForm(user)
            return render(request, 'account/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn!")

    messages.error(request, 'Đã có lỗi xảy ra trong quá trình đặt lại mật khẩu. Vui lòng thử lại sau.')
    return redirect("index")
