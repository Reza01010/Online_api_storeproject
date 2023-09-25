from django.urls import path
from products.views import contact_us_view, my_account_view, SearchView


from . import views

urlpatterns = [
    path('', views.home_page_view, name='home'),
    path('contact_us/', contact_us_view, name='contactus'),
    path('my_account/', my_account_view, name='myaccount'),
    path('search/', SearchView, name='search'),
    
]