from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'ornek@eposta.com',
            'class': 'form-input',
            'autocomplete': 'email',
        })
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Kullanıcı adınız',
                'class': 'form-input',
                'autocomplete': 'username',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Şifreniz (en az 6 karakter)',
            'class': 'form-input',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Şifrenizi tekrar girin',
            'class': 'form-input',
            'autocomplete': 'new-password',
        })

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Kullanıcı adınız',
            'class': 'form-input',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Şifreniz',
            'class': 'form-input',
            'autocomplete': 'current-password',
        })
    )
