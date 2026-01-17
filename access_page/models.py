from django.db import models

# Create your models here.

class User(models.Model):
    username=models.CharField(max_length=30)
    email=models.EmailField(unique=True, null=True, blank=True)
    phone_number=models.CharField(max_length=15, unique=True, null=True, blank=True)
    otp_verification=models.CharField(max_length=6)
    password=models.CharField(max_length=150)

