from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

from django.core.validators import RegexValidator

no_html_validator = RegexValidator(
    regex=r'^[^<>]*$',
    message='ممنوع استخدام علامات HTML'
)

class ProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(validators=[no_html_validator])
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_picture']
        
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'كلمة المرور الحالية'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'كلمة المرور الجديدة'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'تأكيد كلمة المرور الجديدة'})
    )

