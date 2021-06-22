from django.test import TestCase
from django.urls import reverse

from smartphone_app.models import Ptt

import json

class HomeViewTest(TestCase):

    def setUp(self):
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
        
    def test_data_len_is_ten(self):
        resp = self.client.get(reverse('home_api'))
        len_data = len(json.loads(str(resp.content))["products"])
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len_data, 10)