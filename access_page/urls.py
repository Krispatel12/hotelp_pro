from django.urls import path
from . import views

# access_page/urls.py
urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('send-email-otp/', views.send_email_otp, name='send_email_otp'),
    path('verify-email-otp/', views.verify_email_otp, name='verify_email_otp'),
]

