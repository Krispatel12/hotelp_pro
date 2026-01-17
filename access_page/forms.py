from django import forms
from .models import User

Auth_Choices = [
    ('email','Email'),
    ('phone','Phone Number'),
]

class UserRegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    auth_type = forms.ChoiceField(choices=Auth_Choices, widget=forms.Select())
    email = forms.EmailField(required=False)
    phone_number = forms.CharField(required=False, max_length=15)

    class Meta:
        model = User
        fields = ['auth_type','username', 'email', 'phone_number','otp_verification','password']

    def clean(self):
        cleaned_data = super().clean()
        auth_type = cleaned_data.get("auth_type")
        email = cleaned_data.get("email")
        phone_number = cleaned_data.get("phone_number")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Password match
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

        # Email validation
        if auth_type == 'email' and not email:
            self.add_error('email', "Email is required")

        # Phone validation
        if auth_type == 'phone' and not phone_number:
            self.add_error('phone_number', "Phone number is required")

        return cleaned_data
