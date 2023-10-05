from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase




class AppAccountsTest(APITestCase):
    def setUp(self):
        self.superuser = get_user_model().objects.create_superuser(username='john', email='john@snow.com', )
        self.superuser.set_password('johnpassword')
        self.superuser.save()
        self.client.login(username='john', password='johnpassword')
        
