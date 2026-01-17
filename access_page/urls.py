from django.urls import path,include
from . import views

# access_page/urls.py
urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('send-email-otp/', views.send_email_otp, name='send_email_otp'),
    path('verify-email-otp/', views.verify_email_otp, name='verify_email_otp'),
    path('send-whatsapp-otp/', views.send_whatsapp_otp_view, name='send_whatsapp_otp'),
    path('verify-whatsapp-otp/', views.verify_whatsapp_otp, name='verify_whatsapp_otp'),
    path('login/', views.login_view, name='login'),
    path('forgetpassword/', views.forgetpassword_view, name='forgetpassword'),
    path('send-reset-otp/', views.send_reset_otp_view, name='send_reset_otp'),
    path('verify-reset-otp/', views.verify_reset_otp_view, name='verify_reset_otp'),
    path('reset-password-complete/', views.reset_password_complete_view, name='reset_password_complete'),
    path('customer/',include('customer.urls')),
]

