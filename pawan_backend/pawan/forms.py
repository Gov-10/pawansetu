from django import forms
from .models import PawanUser
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import requests
from django.conf import settings
import uuid

class RecaptchaWidget(forms.Widget):
   def render(self, name, value, attrs=None, renderer=None):
        return f'''
        <script src="https://www.google.com/recaptcha/api.js" async defer></script>
        <button class="submit-btn g-recaptcha"
                data-sitekey="{settings.RECAPTCHA_PUBLIC_KEY}"
                data-callback="onSubmit"
                data-action="submit">
            Register
        </button>
        '''
class RecaptchaField(forms.CharField):
    widget = RecaptchaWidget
    
    def __init__(self, *args, **kwargs):
        kwargs['required'] = True
        super().__init__(*args, **kwargs)
    
    def validate(self, value):
        super().validate(value)
        if not self.verify_recaptcha(value):
            raise ValidationError('reCAPTCHA verification failed')
    
    def verify_recaptcha(self, token):
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': token
        }
        
        try:
            response = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data=data,
                timeout=10
            )
            result = response.json()
            return result.get('success', False)
        except:
            return False
class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    recaptcha_token = RecaptchaField(required=True)
    class Meta:
        model = PawanUser
        fields = ('username', 'email')
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email_token = uuid.uuid4()
        user.is_verified = False
        if commit:
            user.save()
        return user