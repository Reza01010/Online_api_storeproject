from django.test import TestCase
from django.shortcuts import reverse

class TestPage(TestCase):
    def test_home_url_and_urlname(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_aboutus_url_and_urlname(self):
        response = self.client.get('/aboutus/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('aboutus'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/aboutus.html')
