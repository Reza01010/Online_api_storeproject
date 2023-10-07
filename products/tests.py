from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import Product, Contact_us, Comment, UserFavorite
from orders.models import Order,OrderItem

class SearchViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.product_1 = Product.objects.create(title="1title",description="1description",price=10.01)
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')


    def test_search_view_with_query(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('search')
        response = self.client.get(url, {'query': self.product_1.title})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['description'], self.product_1.description)

        response_2 = self.client.get(url, {'query': self.product_1.description})
        self.assertEqual(response_2.status_code, status.HTTP_200_OK)
        self.assertEqual(response_2.data[0]['title'], self.product_1.title)
    
    def test_search_view_with_querynon(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('search')
        response = self.client.get(url, {'query': 'nontest'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_search_view_without_query(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class ProductListViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.product_1 = Product.objects.create(title="1title",description="1description",price=10.01)
        self.product_2 = Product.objects.create(title="2title",description="2description",price=20.02)
        self.product_3 = Product.objects.create(title="3title",description="3description",price=30.03)
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')


    def test_product_list_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product:product_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], self.product_1.title)
        self.assertEqual(response.data[1]['title'], self.product_2.title)
        self.assertEqual(response.data[2]['title'], self.product_3.title)
    
    def test_product_list_view_badrequest(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product:product_list')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ProductDetailViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.product_1 = Product.objects.create(title="1title",description="1description",price=10.01)
        self.comment_1 = Comment.objects.create(product=self.product_1, author=self.user, body="ccCCccCCccCC", starts=1)
        
    def test_product_detail_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product:product_detail', args=[self.product_1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.product_1.title)
        self.assertEqual(response.data['comments'][0]['body'], self.comment_1.body)
        self.assertEqual(int(response.data['comments'][0]['starts']), self.comment_1.starts)


class CommentCreateViewTestCase(APITestCase):
    def test_comment_create_view(self):
        client = APIClient()
        user = get_user_model().objects.create_user(username='testuser', password='testpass')
        client.force_authenticate(user=user)
        product = Product.objects.create(title='Test Product', description='Test Description', active=True,price=30.03)
        url = reverse('product:product_comment', args=[product.pk])
        data = {
            'product': product.pk,
            'body': 'Test Comment',
            'starts': 5,
        }
        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_comment_create_view_notlogin(self):
        client = APIClient()
        product = Product.objects.create(title='Test Product', description='Test Description', active=True,price=30.03)
        url = reverse('product:product_comment', args=[product.pk])
        data = {
            'product': product.pk,
            'body': 'Test Comment',
            'starts': 5,
        }
        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_create_view_badhttpmethod(self):
        client = APIClient()
        user = get_user_model().objects.create_user(username='testuser', password='testpass')
        client.force_authenticate(user=user)
        product = Product.objects.create(title='Test Product', description='Test Description', active=True,price=30.03)
        url = reverse('product:product_comment', args=[product.pk])
        data = {
            'product': product.pk,
            'body': 'Test Comment',
            'starts': 5,
        }
        response = client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class FavoritesViewTestCase(APITestCase):
    def test_favorites_view(self):
        client = APIClient()
        user = get_user_model().objects.create_user(username='testuser', password='testpass')
        product_1 = Product.objects.create(title="1title",description="1description",price=10.01)
        UserFavorite.objects.create(user=user, product=product_1)
        client.force_authenticate(user=user)
        url = reverse('product:favorites')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], product_1.pk)


class FavoriteAddViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.product_1 = Product.objects.create(title="1title",description="1description",price=10.01)
        self.product_2 = Product.objects.create(title="2title",description="2description",price=20.02)
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        UserFavorite.objects.create(user=self.user, product=self.product_1)

    def test_favorite_add1_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product:favorite_add', args=[self.product_1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'Product already in favorites.'})
    def test_favorite_add2_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product:favorite_add', args=[self.product_2.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'Favorite added successfully.'})
    def test_favorite_addnon_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('product:favorite_add', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



class ContactUsViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
    

    def test_contact_us_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('contactus')
        response = self.client.post(url, data={
            'mesej': 'Test Message',
            'phone_number': '1234567890',
            'email': 'test@example.com',
            'name': 'Test User'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'OK')
    
    def test_contact_us_view_notvalid(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('contactus')
        response = self.client.post(url, data={
            'phone_number': '1234567894440',
            'email': 'tm',
            'name': f'Test User > {"y"*1000}'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('email', response.data)
        self.assertIn('phone_number', response.data)
        self.assertIn('mesej', response.data)
        self.assertNotIn('OK', response.data)

    def test_contact_us_view_with_existing_comment(self):
        self.client.force_authenticate(user=self.user)
        Contact_us.objects.create(user=self.user, mesej= '1Test Message',
                                            phone_number= '1111111190',
                                            email= 'test1111@example.com',
                                            name= '1Test User')
        url = reverse('contactus')
        response = self.client.post(url, data={
            'mesej': '2Test Message',
            'phone_number': '2222222290',
            'email': 'test2222@example.com',
            'name': '2Test User'
        })
        self.assertEqual(response.status_code, status.HTTP_408_REQUEST_TIMEOUT)
        self.assertIn('You can only comment every Remaining time', response.data['message'])


class MyAccountViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
    

    def test_my_account_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('myaccount')
        response = self.client.post(url, data={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'username': 'johndoe'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['my_account'], {'email': 'john@example.com',
                                                        'first_name': 'John',
                                                          'last_name': 'Doe',
                                                            'username': 'testuser',})
        self.assertEqual(response.data['note'],  "These fields are already filled  ==> [['username']] ")

    def test_my_account_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('myaccount')
        response = self.client.post(url, data={
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['my_account'], {'first_name': 'John',
                                                          'last_name': 'Doe',
                                                            'username': 'testuser',
                                                             'email': '',})
        self.assertEqual(response.data['note1'],  "These fields are already filled  ==> [['username']] ")
        self.assertEqual(response.data['note2'],  "These fields are empty  ==> [['email']] ")

    def test_my_account_view_with_existing_fields(self):
        self.client.force_authenticate(user=self.user)
        self.user.first_name = 'John'
        self.user.save()
        url = reverse('myaccount')
        response = self.client.post(url, data={
            'first_name': 'khjkgh',
            'last_name': 'Dogjge',
            'email': '.com',
            'username': 'janedoe'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_my_account_view_get(self):
        product_1 = Product.objects.create(title="1title",description="1description",price=10.01)
        UserFavorite.objects.create(user=self.user, product=product_1)
        order = Order.objects.create(user=self.user, is_paid=False, first_name='ramin', last_name='hhhh', phone_number='09887654345', address='gggf seerg erg', order_notes='fereeter')
        order_item = OrderItem.objects.create(order=order, product=product_1, quantity=2, price=int(product_1.price+product_1.price))

        self.client.force_authenticate(user=self.user)
        url = reverse('myaccount')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('listfe', response.data)
        self.assertIn('order', response.data)
        self.assertIn('myaccount', response.data)
        self.assertEqual(response.data['listfe'][0]['id'], product_1.pk)
        self.assertEqual(response.data['order'][0]['items'][0]['product'], order_item.product.id)
        self.assertEqual(response.data['order'][0]['items'][0]['quantity'], order_item.quantity)
        self.assertEqual(response.data['order'][0]['items'][0]['price'], order_item.price)
        self.assertEqual(response.data['order'][0]['phone_number'], order.phone_number)
        self.assertEqual(response.data['order'][0]['order_notes'], order.order_notes)
        self.assertEqual(response.data['myaccount'], {'first_name': '', 'last_name': '', 'email': '', 'username': 'testuser'})
