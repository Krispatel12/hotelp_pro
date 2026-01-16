from django.shortcuts import render
from .forms import UserRegisterForm
# Create your views here.
def signup_view(request):
    form=UserRegisterForm()
    return render(request,'access_page/sign_up.html',{'form':form})