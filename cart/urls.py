from django.urls import path

from .views import (cart_detail_view, AddToCartView as add_to_cart_view, remove_from_cart, clear_cart, )


app_name = "cart"


urlpatterns = [
    path('', cart_detail_view, name='cart_detail'),
    path('add/', add_to_cart_view.as_view(), name='cart_add'),
    path('remove/<int:product_id>/', remove_from_cart, name='cart_remove'),
    path('clear/', clear_cart, name='cart_clear'),
]
