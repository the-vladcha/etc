from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from pvn.settings import EMAIL_HOST_USER
from .forms import LoginForm, RegistrationForm

from .models import MyUser

from django.urls import reverse
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import account_activation_token


class LoginView(View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {'form': form}
        return render(request, 'user/login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
        context = {'form': form}
        return render(request, 'user/login.html', context)


class RegistrationView(View):
    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        context = {'form': form}
        return render(request, 'user/register.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.is_active = False
            new_user.save()
            MyUser.objects.create(
                user=new_user,
                phone_number=form.cleaned_data['phone_number'],
            )

            domain = get_current_site(request).domain
            uidb64 = urlsafe_base64_encode(force_bytes(new_user.pk))

            link = reverse('activate',
                           kwargs={'uidb64': uidb64, 'token': account_activation_token.make_token(new_user)})
            activate_url = 'http://' + domain + link
            email_subject = 'Активация аккаунта'
            email_body = 'Привет ' + new_user.username + ' быстро подтведи регистрацию!\n' + activate_url
            email = EmailMessage(
                email_subject,
                email_body,
                EMAIL_HOST_USER,
                [new_user.email],
            )
            email.send(fail_silently=False)
            return redirect('home')
        context = {'form': form}
        return render(request, 'user/register.html', context)


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login' + '?message=' + 'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            pass
        return redirect('home')


def index(request):
    return render(request, template_name='user/index.html')
