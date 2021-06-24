from django.test import TestCase
from django.urls import reverse

from smartphone_app.models import Ptt

import json

class HomeViewTest(TestCase):

    @classmethod
    def setUp(cls):
        #Create phones
        number_of_phones = 10
        for phone_num in range(number_of_phones):
            Ptt.objects.create(title='iPhone 12', storage = phone_num,)

    def test_view_url_exists_at_desired_location(self): 
        resp = self.client.get('/api/v1/home') 
        self.assertEqual(resp.status_code, 200)  
           
    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('home_api'))
        self.assertEqual(resp.status_code, 200)
        
    def test_datail_page_template(self):
        resp = self.client.get('/detail/iPhone+12/128')
        self.assertTemplateUsed(resp, "detail.html")