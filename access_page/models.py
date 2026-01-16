from django.db import models

# Create your models here.

class User(models.Model):
    username=models.CharField(max_length=30)
    email=models.EmailField(unique=True)
    phone_number=models.CharField(max_length=15)
    otp_verification=models.CharField(max_length=6)
    password=models.CharField(max_length=150)

