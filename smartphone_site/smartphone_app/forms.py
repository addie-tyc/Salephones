from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Ptt

import requests
from bs4 import BeautifulSoup
from datetime import datetime

from .util import get_phones

class SignUpForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    username = forms.CharField(
        label="帳號",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="密碼(至少 8 位、英數混合，勿使用 帳號 或 email 相似字)",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="密碼確認",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    username = forms.CharField(
        label="帳號",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )



class SaleForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    phones = get_phones()
    title_choices = tuple([ (p, p) for p in phones ])
    title = forms.ChoiceField(label="手機名稱", widget=forms.Select(attrs={'class': 'form-control'}), choices=title_choices, required=True)
    storage_choices = [32, 64, 128, 256, 512, 1024]
    storage_choices = [ (i,i) for i in storage_choices ]
    storage = forms.ChoiceField(label="手機容量（GB）", widget=forms.Select(attrs={'class': 'form-control'}), choices=storage_choices, required=True)
    price = forms.IntegerField(label="價格", widget=forms.NumberInput(attrs={'class': 'form-control'}), min_value=1, required=True)
    new_choices = [ (0, "已使用"), (1, "全新") ]
    new = forms.ChoiceField(label="已使用 或 全新", widget=forms.Select(attrs={'class': 'form-control'}), choices=new_choices, required=True)
    sold = forms.IntegerField(widget=forms.HiddenInput(attrs={'class': 'form-control'}), initial=0, required=True)
    account = forms.CharField(widget=forms.HiddenInput(attrs={'class': 'form-control'}), initial="0", required=True)
    email = forms.CharField(widget=forms.HiddenInput(attrs={'class': 'form-control'}), initial="0", required=True)
    box = forms.CharField(label="盒裝內容", widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    status = forms.CharField(label="物品狀況", widget=forms.Textarea(attrs={'class': 'form-control'}), required=True)
    created_at = forms.CharField(widget=forms.HiddenInput(attrs={'class': 'form-control'}), initial=datetime.now(), required=True)
    source = forms.CharField(widget=forms.HiddenInput(attrs={'class': 'form-control'}), initial="native", required=True)
    images = forms.FileField(label="商品照片（最多 4 張）", 
                             widget=forms.FileInput(
                                 attrs={'class': 'form-control', 'multiple': True, 'accept':"image/jpg, image/jpeg, image/png", 'id':"images"}),
                             required=True)
    

    class Meta:
        model = Ptt
        fields = ('title', 'storage', 'price', 'new', 'sold', 
                  'account',  'box', 'status', 'created_at', 'source', 'images')
                  # default value: sold, account, created_at, source