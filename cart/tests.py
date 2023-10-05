from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import Cart, CartItem
from products.models import Product
from products.serializers import CartSerializer
from requests.auth import HTTPBasicAuth


class CartDetailViewTestCase(APITestCase):
    def setUp(self):
        self.product_1 = Product.objects.create(title="1title",description="1description",price=10.01)

        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(cart=self.cart, product_id=self.product_1.id, quantity=2)

    def test_get_cart_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('cart:cart_detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cart'], CartSerializer(self.cart).data)

    def test_post_cart_detail(self):
        print("^"*500, self.product_1.id)
        self.client.force_authenticate(user=self.user)
        url = reverse('cart:cart_detail')
        data = {
                    "items": [
                        {
                            "product": self.product_1.id,
                            "quantity": 3
                        }
                    ]
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cart']['items'][0]['quantity'], 3)

    def test_delete_cart_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('cart:cart_detail')
        data = {'product_ids': [self.product_1.id]}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cart']['items'], [])

    def test_delete_cart_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('cart:cart_detail')
        data = {'product_ids': [], "remove_all":True}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cart']['items'], [])