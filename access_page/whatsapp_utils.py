import requests
from django.conf import settings
import json

def send_whatsapp_msg(phone_number, message_body):
    """
    Sends a text message to the specified phone number using WhatsApp Cloud API.
    
    Args:
        phone_number (str): The recipient's phone number with country code (e.g., '919876543210').
        message_body (str): The text message to send.
        
    Returns:
        dict: A dictionary containing 'status' and 'message'/'data'.
    """
    try:
        api_url = settings.WHATSAPP_API_URL
        api_key = settings.WHATSAPP_API_KEY
        sender_number = settings.WHATSAPP_SENDER_NUMBER # Might be used in URL or body depending on setup, usually URL includes Phone Number ID

        if not api_url or not api_key:
            return {
                'status': 'error',
                'message': 'WhatsApp API credentials are not configured in settings.'
            }

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        # Payload for a standard text message
        # Note: For business-initiated conversations (outside 24h window), templates are required.
        # This implementation assumes we can send text messages (within 24h window) or the user handles templates.
        # If templates are needed, the payload structure changes. 
        # For OTPs, usually a template "authentication" category is used.
        
        # Here we assume a free-form text message for simplicity/testing or if session is active.
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "from": sender_number,
            "type": "text",
            "text": {
                "body": message_body
            }
        }

        response = requests.post(api_url, headers=headers, json=payload)
        
        if response.status_code in [200, 201]:
            return {
                'status': 'success',
                'data': response.json()
            }
        else:
            print(f"Failed WhatsApp Request URL: {api_url}") # Debug log
            return {
                'status': 'error',
                'message': f"WhatsApp API Error: {response.status_code} - URL: {api_url} - {response.text}"
            }

    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f"Network error processing WhatsApp request: {str(e)}"
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Unexpected error submitting WhatsApp request: {str(e)}"
        }

def send_whatsapp_otp(phone_number, otp):
    """
    Helper function specifically to send an OTP.
    
    Args:
        phone_number (str): Recipient phone number.
        otp (str): The OTP code to send.
    """
    message = f"Your HotelPro verification code is: {otp}"
    return send_whatsapp_msg(phone_number, message)
