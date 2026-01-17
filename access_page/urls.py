from django.urls import path
from . import views

# access_page/urls.py
urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('send-email-otp/', views.send_email_otp, name='send_email_otp'),
    path('verify-email-otp/', views.verify_email_otp, name='verify_email_otp'),
    path('send-whatsapp-otp/', views.send_whatsapp_otp_view, name='send_whatsapp_otp'),
    path('verify-whatsapp-otp/', views.verify_whatsapp_otp, name='verify_whatsapp_otp'),
]

