from django.urls import path

from .views import (cart_detail_view, AddToCartView as add_to_cart_view,  )


app_name = "cart"


urlpatterns = [
    path('', cart_detail_view, name='cart_detail'),
    path('add/', add_to_cart_view.as_view(), name='cart_add'),

]
