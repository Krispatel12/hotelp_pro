from django.shortcuts import render, redirect
from .models import Review
from django.contrib import messages

# Create your views here.

def landing(request):
    return render(request, 'core/landing.html')

def features(request):
    return render(request, 'core/features.html')

def how_it_works(request):
    return render(request, 'core/how_it_works.html')

def reviews_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if name and rating and comment:
            Review.objects.create(name=name, rating=rating, comment=comment)
            messages.success(request, 'Thank you for your review!')
            return redirect('reviews')
            
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'core/reviews.html', {'reviews': reviews})