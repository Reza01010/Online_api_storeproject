from django.urls import path
from products.views import contact_us_view, my_account_view, search_view


from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(),name='home'),
    path('aboutus/', views.AboutUsPagesView.as_view(), name='aboutus'),
    path('contact_us/', contact_us_view, name='contactus'),
    path('my_account/', my_account_view, name='myaccount'),
    path('search/', search_view, name='search'),
    
]