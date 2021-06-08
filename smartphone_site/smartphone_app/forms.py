from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Ptt

import requests
from bs4 import BeautifulSoup
from datetime import datetime

class SignUpForm(UserCreationForm):
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
    username = forms.CharField(
        label="帳號",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


def get_phones():
    url = "https://en.wikipedia.org/wiki/List_of_Android_smartphones"
    resp = requests.get(url, verify=False)
    soup = BeautifulSoup(resp.text, "html.parser")

    tables = soup.find_all("table", class_="wikitable")
    rows = []
    for i in tables:
        rows.extend(i.select("tbody tr th"))

    phones = [a.text.partition("(")[0].strip() for a in rows]
    phones = [ p for p in phones if len(p.split()) > 1]

    brands = set()
    for p in phones:
        brands.add(p.split(" ")[0])
    brands = list(brands)
    brands = sorted(brands)
    for b in range(len(brands)):
        if brands[b] == "Asus":
            brands = brands[b:]
            break

    phone_list = []
    for b in brands:
        if b == "Samsung":
            for p in phones:
                if p.split(" ")[0] == b:
                    if "/" in p:
                        p_lst = p.split("/")
                        for series in p_lst[1:]:
                            sub_p = p_lst[0].replace("5G", "").strip()
                            if series == "+":
                                phone = sub_p + series
                            else:
                                phone = sub_p + " " + series
                            if len(phone) > 0:
                                phone_list.append(phone)
                        phone_list.append(sub_p)
                    else:
                        phone = p.replace("5G", "").strip()
                        if len(phone) > 0:
                            phone_list.append(phone)
        elif b == "POCO":
            for p in phones:
                if p.split(" ")[0] == b:
                    phone = p.replace("5G", "").strip()
                    if len(phone) > 0:
                        phone_list.append(phone)

        elif b == "Pixel":
            for p in phones:
                if p.split(" ")[0] == b:
                    phone = p.replace("5G", "").strip()
                    if len(phone) > 0:
                        phone_list.append(phone)
        else:
            for p in phones:
                if p.split(" ")[0] == b:
                    if "/" in p:
                        p_lst = p.split("/")
                        for series in p_lst[1:]:
                            sub_p = p_lst[0].replace("5G", "").strip()
                            if series == "+":
                                phone = sub_p + series
                            else:
                                phone = sub_p + " " + series
                            if len(phone) > 0:
                                phone_list.append(phone)
                        phone_list.append(sub_p)
                    else:
                        phone = p.replace("5G", "").strip()
                        if len(phone) > 0:
                            phone_list.append(phone)
                        phone_list.append(phone)
    phone_list.append("Asus ROG Phone 2")

    url = "https://www.theiphonewiki.com/wiki/List_of_iPhones"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    table = soup.find("div", id="toc")
    iphones = []
    for span in table.select("ul li span"):
        if "iPhone" in str(span):
            if ("SE" in str(span)) and ("1" in str(span)):
                iphones.append("iPhone SE")
            elif ("SE" in str(span)) and ("2" in str(span)):
                iphones.append("iPhone SE2")
            else:
                iphones.append(span.text)
    iphones.remove("iPhone")
    phone_list.extend(iphones)
    phone_set = set()
    for p in phone_list:
        phone_set.add(p)
    phone_list.append("Samsung Galaxy A71")
    phone_list = sorted(list(phone_set))
    phone_list.remove("Asus ROG Phone II")
    phone_list.remove("Release date")
    phone_list.remove("Samsung Galaxy")
    phone_list.remove("Samsung Galaxy A51 A71")
    phone_list.remove("Samsung Galaxy A51 A71 5G")
    phone_list.remove("Samsung Galaxy A52 A52 5G")
    return phone_list

class SaleForm(forms.ModelForm):
    phones = get_phones()
    title_choices = tuple([ (p, p) for p in phones ])
    title = forms.ChoiceField(label="手機名稱", widget=forms.Select(attrs={'class': 'form-control'}), choices=title_choices, required=True)
    storage_choices = [32, 64, 128, 256, 512, 1024]
    storage_choices = [ (i,i) for i in storage_choices ]
    storage = forms.ChoiceField(label="手機容量（GB）", widget=forms.Select(attrs={'class': 'form-control'}), choices=storage_choices, required=True)
    price = forms.IntegerField(label="價格", widget=forms.NumberInput(attrs={'class': 'form-control'}), required=True)
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
                             required=False)
    

    class Meta:
        model = Ptt
        fields = ('title', 'storage', 'price', 'new', 'sold', 
                  'account',  'box', 'status', 'created_at', 'source', 'images')
                  # default value: sold, account, created_at, source