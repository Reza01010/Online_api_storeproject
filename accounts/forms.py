from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth import get_user_model

from captcha.fields import CaptchaField
from allauth.account.forms import LoginForm, SignupForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'Seller')


class CustomLoginForm(LoginForm):
    captcha = CaptchaField()


class CustomSignupForm(SignupForm):
    captcha = CaptchaField()
