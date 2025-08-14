from django.shortcuts import render
from .forms import SignupForm, LoginForm
from .models import PawanUser
from django.conf import settings
from django.shortcuts import render, redirect
from .tokens import account_activation_token
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login, authenticate, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
def verify_recaptcha(token):
    """Helper function to verify reCAPTCHA"""
    import requests
    from django.conf import settings
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


def ActivateEmail(request, user, to_email):
    mail_subject = "Activate your account"
    message = render_to_string("template_activate.html", {
        'user': user.username, 
        'domain': get_current_site(request).domain, 
        'uid': urlsafe_base64_encode(force_bytes(user.pk)), 
        'token': account_activation_token.make_token(user), 
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to = [to_email])
    return email.send()

def signup(request):
    if request.method == "POST":
        post_data = request.POST.copy()
        if 'g-recaptcha-response' in request.POST:
            post_data['recaptcha_token'] = request.POST.get('g-recaptcha-response')
        form = SignupForm(post_data)
        if form.is_valid():
            pawanuser = form.save(commit=False)
            pawanuser.is_active = False
            pawanuser.save()
            if ActivateEmail(request, pawanuser, form.cleaned_data.get('email')):
                return render(request, 'email_verification_sent.html')
            else:
                print("error sending email")
        else:
            for error in list(form.errors.values()):
                print(error)
    else:
        form = SignupForm()
    return render(request, 'sign_up.html', {'form': form, 'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        pawan = PawanUser.objects.get(pk=uid)
    except:
        pawan = None
    if pawan is not None and account_activation_token.check_token(pawan, token):
        pawan.is_active= True
        pawan.is_verified = True
        pawan.save()
        return redirect('sign_in')
    else:
        print("activation failed")
    return redirect('home')

def home(request):
    return render(request, "home.html")

@csrf_exempt
def signin(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            token = request.POST.get('g-recaptcha-response')
            if not verify_recaptcha(token):
                form.add_error(None, "reCaptcha failed")
                return render(request, 'login.html', {'form':form, 'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY})
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            user = authenticate(request, username=username, password= password)
            if user is not None:
                if not user.is_verified:
                    form.add_error(None, "Please verify your email before logging in")
                    return render(request, 'login.html', {'form':form, 'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY})
                login(request, user)
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                return redirect(f"{settings.NEXTJS_FRONTEND_URL}/home?token={access_token}")
            else:
                form.add_error(None, "Invalid username or password")
        else:
            form =LoginForm()
        return render(request, 'login.html', {'form':form, 'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form':form, 'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    if user.is_authenticated:
        return Response({
            'username': user.username,
            'email': user.email,
            'is_verified': user.is_verified
        })
    return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

