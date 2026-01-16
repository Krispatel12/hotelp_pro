from django.shortcuts import render
from .forms import UserRegisterForm
import random
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


# Create your views here.
def signup_view(request):
    form=UserRegisterForm()
    return render(request,'access_page/sign_up.html',{'form':form})

@csrf_exempt
def send_email_otp(request):
    email = request.GET.get('email')

    if not email:
        return JsonResponse({'status': 'error', 'message': 'Email required'}, status=400)

    otp = random.randint(100000, 999999)

    # Save OTP in session (simple & safe)
    request.session['email_otp'] = str(otp)
    request.session['email_otp_email'] = email

    send_mail(
        subject='Your OTP Verification',
        message=f'Your OTP is {otp}. It is valid for 5 minutes.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False
    )

    return JsonResponse({'status': 'success', 'message': 'OTP sent successfully'})
@csrf_exempt
def verify_email_otp(request):
    email = request.GET.get('email')
    otp = request.GET.get('otp')

    if not email or not otp:
        return JsonResponse({'status': 'error', 'message': 'Email and OTP required'}, status=400)

    session_otp = request.session.get('email_otp')
    session_email = request.session.get('email_otp_email')

    if session_otp and session_email == email:
        if otp == session_otp:
            return JsonResponse({'status': 'success', 'message': 'OTP verified'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid OTP'})
    else:
        return JsonResponse({'status': 'error', 'message': 'OTP expired or not sent'})
