from django.shortcuts import render

# Create your views here.
def customer_dashboard(request):
    return render(request, 'customer/customer_dashboard.html')
    