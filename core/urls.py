from django.urls import path,include
from . import views
urlpatterns=[
    path('',views.landing,name='landing'),
    path('features/', views.features, name='features'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('reviews/', views.reviews_view, name='reviews'),
    path('sign-up/',include('access_page.urls'))
]