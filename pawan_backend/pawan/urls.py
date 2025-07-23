from django.urls import path
from . import views
urlpatterns = [
    path("sign_up/" , views.signup, name="sign_up"), 
    path("home/" , views.home, name="home"), 
    path("login/" , views.signin, name="login"),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'), 
    path('user/', views.user_profile, name='user_profile'),

]
