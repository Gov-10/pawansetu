from django.urls import path
from . import views
urlpatterns = [
    path("sign_up/" , views.signup, name="sign_up"), 
    path("home/" , views.home, name="home"), 
    path("login/" , views.login, name="login"),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'), 

]
