from django.shortcuts import render
from .forms import UserRegisterForm
from .whatsapp_utils import send_whatsapp_otp
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
    try:
        email = request.GET.get('email', '').strip()
        
        if not email:
            return JsonResponse({
                'status': 'error',
                'message': 'Email is required'
            }, status=400)

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Save OTP in session
        request.session['email_otp'] = str(otp)
        request.session['email_otp_email'] = email
        request.session.set_expiry(300)  # 5 minutes

        try:
            send_mail(
                subject='Your OTP Verification',
                message=f'Your OTP is {otp}. It is valid for 5 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False
            )
            
            # For development - remove in production
            print(f"OTP for {email}: {otp}")
            
            return JsonResponse({
                'status': 'success',
                'message': 'OTP sent successfully',
                'otp': str(otp)  # Remove in production
            })
            
        except Exception as e:
            print(f"Email sending error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to send OTP. Please try again later.'
            }, status=500)
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }, status=500)

@csrf_exempt
def send_whatsapp_otp_view(request):
    try:
        phone_number = request.GET.get('phone_number', '').strip()
        
        if not phone_number:
            return JsonResponse({
                'status': 'error',
                'message': 'Phone number is required'
            }, status=400)

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Save OTP in session
        request.session['whatsapp_otp'] = str(otp)
        request.session['whatsapp_otp_phone'] = phone_number
        request.session.set_expiry(300)  # 5 minutes

        # Send OTP via WhatsApp
        result = send_whatsapp_otp(phone_number, str(otp))
        
        if result.get('status') == 'success':
            # For development - remove in production
            print(f"WhatsApp OTP for {phone_number}: {otp}")
            
            return JsonResponse({
                'status': 'success',
                'message': 'OTP sent successfully to WhatsApp',
                'otp': str(otp)  # Remove in production
            })
        else:
            return JsonResponse(result, status=500)
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Unexpected error: {str(e)}")
        print(error_details)
        return JsonResponse({
            'status': 'error',
            'message': f'An unexpected error occurred: {str(e)}'
        }, status=500)

@csrf_exempt
def verify_whatsapp_otp(request):
    phone = request.GET.get('phone')
    otp = request.GET.get('otp')

    if not phone or not otp:
        return JsonResponse({'status': 'error', 'message': 'Phone and OTP required'}, status=400)

    session_otp = request.session.get('whatsapp_otp')
    session_phone = request.session.get('whatsapp_otp_phone')

    if session_otp and session_phone == phone:
        if otp == session_otp:
            return JsonResponse({'status': 'success', 'message': 'OTP verified'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid OTP'})
    else:
        return JsonResponse({'status': 'error', 'message': 'OTP expired or not sent'})

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
