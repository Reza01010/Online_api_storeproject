from django.urls import path

from .views import (OrderDeleteView, OrderUnpaidView, OrderCreateView, OrderContinueView)


urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('unpaid/', OrderUnpaidView.as_view(), name='order_unpaid'),
    path('delete/<int:pk>/', OrderDeleteView.as_view(), name='order_delete'),
    path('continue/<int:pk>/', OrderContinueView.as_view(), name='order_continue'),

]
