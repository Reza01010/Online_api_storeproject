from django.test import TestCase
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import Order, OrderItem
from cart.models import Cart,CartItem
from products.models import Product
from products.serializers import OrderSerializer_e
from rest_framework.test import APITestCase, APIRequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from .views import (OrderDeleteView, OrderUnpaidView, OrderCreateView, OrderContinueView)
from rest_framework.test import force_authenticate
from products.serializers import OrderSerializer_e


class OrderCreateViewTestCase(APITestCase):
    def setUp(self):
        self.product_1 = Product.objects.create(title="1title",description="1description",price=10.01)
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(cart=self.cart, product_id=self.product_1.id, quantity=2)

    def test_order_create_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('order_create')
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "1234567890",
            "address": "123 Main St",
            "order_notes": "Some notes",
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(self.client.session['order_id'], Order.objects.get(id=self.client.session['order_id']).id)
        self.assertEqual(response.url, "/payment/process/")

    def test_order_create_view_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('order_create')
        data = {
            "firstname": "John",
            "phone_number": "",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('serializer_errors', response.data)
        self.assertIn('serializer_error_messages', response.data)


class OrderUnpaidViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')

    def test_order_unpaid_view(self):
        self.client.force_authenticate(user=self.user)
        self.product_1 = Product.objects.create(title="1title",description="1description",price=10.01)
        self.order = Order.objects.create(user=self.user, is_paid=False, first_name='ramin', last_name='hhhh', phone_number='09887654345', address='gggf seerg erg', order_notes='fereeter')
        self.order_item = OrderItem.objects.create(order=self.order, product=self.product_1, quantity=2, price=self.product_1.price)
        
        url = reverse('order_unpaid')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('order_unpaid_id', response.data)

    def test_order_unpaid_view_no_order(self):
        Order.objects.filter(user=self.user).delete

        self.client.force_authenticate(user=self.user)
        url = reverse('order_unpaid')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual({'message': 'Order not found'}, response.data)


class OrderDeleteViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.product_1 = Product.objects.create(title="1title",description="1description",price=10.01)
        self.order = Order.objects.create(user=self.user, is_paid=False, first_name='ramin', last_name='hhhh', phone_number='09887654345', address='gggf seerg erg', order_notes='fereeter')
        self.order_item = OrderItem.objects.create(order=self.order, product=self.product_1, quantity=2, price=self.product_1.price)
        

    def test_order_delete_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('order_delete', args=[self.order.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertFalse(Order.objects.filter(pk=self.order.pk).exists())

    def test_order_delete_view_invalid_pk(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('order_delete', args=[999])
        response = self.client.delete(url)
        response = OrderDeleteView.as_view()(response.wsgi_request, pk=999)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderContinueViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.product_1 = Product.objects.create(title="1title",description="1description",price=10.01)
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.order = Order.objects.create(user=self.user, is_paid=False, first_name='ramin', last_name='hhhh', phone_number='09887654345', address='gggf seerg erg', order_notes='fereeter')
        self.order_item = OrderItem.objects.create(order=self.order, product=self.product_1, quantity=2, price=self.product_1.price)
        

    def test_order_continue_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('order_continue', args=[self.order.pk])
        request = self.client.post(url)
        response = OrderContinueView.as_view()(request.wsgi_request, pk=self.order.pk)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(self.client.session['order_id'], Order.objects.get(id=self.client.session['order_id']).id)

    def test_order_continue_view_invalid_pk(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('order_continue', args=[999])
        request = self.client.post(url)
        response = OrderContinueView.as_view()(request.wsgi_request, pk=999)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)