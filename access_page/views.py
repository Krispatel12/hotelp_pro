from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from .forms import UserRegisterForm
from .whatsapp_utils import send_whatsapp_otp
import random
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


# Create your views here.
# Create your views here.
def signup_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone_number')

            # 0. Check for duplicates
            if email and User.objects.filter(email=email).exists():
                 # Account exists, redirect to login as per user request
                 return redirect('login')
            
            if phone and User.objects.filter(phone_number=phone).exists():
                 # Account exists, redirect to login
                 return redirect('login')

            user = form.save(commit=False)
            
            # Ensure empty strings are saved as None to avoid unique constraint violations
            if not user.email:
                user.email = None
            if not user.phone_number:
                user.phone_number = None

            auth_type = form.cleaned_data.get('auth_type')
            
            # 1. Verify OTP was actually checked
            # This is a backend Security Check to prevent bypassing JS
            is_verified = False
            if auth_type == 'email':
                email = form.cleaned_data.get('email')
                session_otp = request.session.get('email_otp')
                session_email = request.session.get('email_otp_email')
                # We assume the user verified it in the previous step (via JS). 
                # Ideally, we should check a "verified" flag in session, but verifying they match NOW is also good.
                user_otp = form.cleaned_data.get('otp_verification')
                if session_otp and session_email == email and user_otp == session_otp:
                     is_verified = True
            
            elif auth_type == 'phone':
                 phone = form.cleaned_data.get('phone_number')
                 session_otp = request.session.get('whatsapp_otp')
                 session_phone = request.session.get('whatsapp_otp_phone')
                 user_otp = form.cleaned_data.get('otp_verification')
                 if session_otp and session_phone == phone and user_otp == session_otp:
                     is_verified = True
            
            if not is_verified:
                form.add_error('otp_verification', "Invalid or expired OTP. Please verify again.")
                return render(request, 'access_page/sign_up.html', {'form': form})
            
            # 2. Hash Password
            user.password = make_password(form.cleaned_data.get('password'))
            
            # 3. Save User
            user.save()
            
            # 4. Clear OTP session
            if auth_type == 'email':
                 if 'email_otp' in request.session: del request.session['email_otp']
            else:
                 if 'whatsapp_otp' in request.session: del request.session['whatsapp_otp']
            
            return redirect('customer_dashboard')
    else:
        form = UserRegisterForm()
    
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

def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username') # Form field name 'username' or 'email' depending on HTML
        password = request.POST.get('password')
        
        if not identifier or not password:
            return render(request, 'access_page/login.html', {'error': 'Please enter both credentials'})
            
        # Find user by Email OR Phone
        user = User.objects.filter(Q(email=identifier) | Q(phone_number=identifier)).first()
        
        if user:
            if check_password(password, user.password):
                # Success
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                return redirect('customer_dashboard') # Ensure 'landing' matches your URL name
            else:
                return render(request, 'access_page/login.html', {'error': 'Invalid password'})
        else:
             return render(request, 'access_page/login.html', {'error': 'Account not found'})

    return render(request,'access_page/login.html')

def forgetpassword_view(request):
    form=UserRegisterForm()
    return render(request,'access_page/forgetpassword.html',{'form':form})

from .models import User
import json

@csrf_exempt
def send_reset_otp_view(request):
    auth_type = request.GET.get('auth_type')
    identifier = request.GET.get('identifier') # email or phone

    if not identifier:
         return JsonResponse({'status': 'error', 'message': 'Identifier required'}, status=400)

    user_exists = False
    if auth_type == 'email':
        if User.objects.filter(email=identifier).exists():
            user_exists = True
    elif auth_type == 'phone':
         if User.objects.filter(phone_number=identifier).exists():
             user_exists = True
    
    if not user_exists:
        # Security: In production, maybe dont reveal user existence. But for this app/debugging:
        return JsonResponse({'status': 'error', 'message': 'User not found with these details'}, status=404)

    # User exists, proceed to send OTP
    otp = random.randint(100000, 999999)
    # 5 min expiry
    request.session.set_expiry(300)

    try:
        if auth_type == 'email':
            request.session['reset_otp'] = str(otp)
            request.session['reset_id'] = identifier
            request.session['reset_type'] = 'email'
            
            send_mail(
                subject='Password Reset OTP',
                message=f'Your Password Reset OTP is {otp}. Valid for 5 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[identifier],
                fail_silently=False
            )
            print(f"Reset Email OTP for {identifier}: {otp}") # Dev log
            return JsonResponse({'status': 'success', 'message': 'OTP sent to email', 'otp': str(otp)})

        elif auth_type == 'phone':
            request.session['reset_otp'] = str(otp)
            request.session['reset_id'] = identifier
            request.session['reset_type'] = 'phone'

            result = send_whatsapp_otp(identifier, str(otp))
            if result.get('status') == 'success':
                 print(f"Reset WhatsApp OTP for {identifier}: {otp}") # Dev log
                 return JsonResponse({'status': 'success', 'message': 'OTP sent to WhatsApp', 'otp': str(otp)})
            else:
                 return JsonResponse(result, status=500)
    
    except Exception as e:
        print(f"Error sending reset OTP: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def verify_reset_otp_view(request):
    otp = request.GET.get('otp')
    session_otp = request.session.get('reset_otp')
    
    if not otp:
        return JsonResponse({'status': 'error', 'message': 'OTP required'}, status=400)
    
    if session_otp and str(otp) == str(session_otp):
        return JsonResponse({'status': 'success', 'message': 'OTP Verified'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid OTP'})

@csrf_exempt
def reset_password_complete_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            password = data.get('password')
            
            identifier = request.session.get('reset_id')
            reset_type = request.session.get('reset_type')

            if not identifier or not password:
                 return JsonResponse({'status': 'error', 'message': 'Session expired or missing data'}, status=400)

            user = None
            if reset_type == 'email':
                user = User.objects.filter(email=identifier).first()
            elif reset_type == 'phone':
                user = User.objects.filter(phone_number=identifier).first()
            
            if user:
                user.password = make_password(password) # Fixed: Hash password!
                user.save()
                
                # Clear session
                if 'reset_otp' in request.session: del request.session['reset_otp']
                if 'reset_id' in request.session: del request.session['reset_id']
                
                return JsonResponse({'status': 'success', 'message': 'Password updated successfully'})
            else:
                return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

        except Exception as e:
             return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
