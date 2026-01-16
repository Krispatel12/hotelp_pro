from django.urls import path,include
from . import views
urlpatterns=[
    path('',views.landing,name='landing'),
    path('sign-up/',include('access_page.urls'))
]