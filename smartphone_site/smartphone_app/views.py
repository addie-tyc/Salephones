from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from bs4 import BeautifulSoup
from django.db.models import Count, FloatField, IntegerField, DateField, Avg, Max, Func, F, Min
from django.db.models.functions import Cast
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from rest_framework import serializers
from django.conf import settings
import boto3


from datetime import datetime, timedelta
import requests
from collections import defaultdict
import time
import os

from .models import Ptt, Landtop, db
from .serializers import PttSerializer, LandtopSerializer, PttDetailSerializer, PttGraphSerializer, ProfileSerializer
from .forms import SignUpForm, LoginForm, SaleForm
import env

# pages

def home_page(request):
    return render(request, 'home.html')

def detail_page(request, title, storage):
    return render(request, 'detail.html')

def profile_page(request):
    if not request.user.is_authenticated:
        return redirect('/smartphone-smartprice/login') 
    return render(request, 'profile.html')

class SignUpView(GenericAPIView):
    queryset = User.objects.all()

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/smartphone-smartprice/home') 
        form = SignUpForm()
        context = {
        'form': form
        }
        return render(request, 'registration/signup.html', context)
    
    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Signed up successfully!')
            redirect('login')
        else:
            messages.error(request, 'Something went wrong. Please try again!')
        return redirect('/smartphone-smartprice/signup') 


class LoginView(GenericAPIView):
    queryset = User.objects.all()

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/smartphone-smartprice/home') 
        form = LoginForm()
        context = {
        'form': form
        }
        return render(request, 'registration/login.html', context)
    
    def post(self, request):
        form = LoginForm(request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect('/smartphone-smartprice/home')  #重新導向到首頁
        else:
            messages.error(request, 'Something went wrong. Please try again!')
        return redirect('/smartphone-smartprice/login') 

class LogoutView(GenericAPIView):
    queryset = User.objects.all()

    def get(self, request):
        if request.user.is_authenticated:
            auth_logout(request)
        return redirect('/smartphone-smartprice/login')

def get_phones():
    url = "https://en.wikipedia.org/wiki/List_of_Android_smartphones"
    resp = requests.get(url)
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

    phone_dict = defaultdict(list)
    for b in brands:
        if b == "Samsung":
            for p in phones:
                if p.split(" ")[0] == b:
                    if "/" in p:
                        p_lst = p.split("/")
                        for series in p_lst[1:]:
                            sub_p = p_lst[0].replace(b + " Galaxy", "").replace("5G", "").strip()
                            if series == "+":
                                phone = sub_p + series
                            else:
                                phone = sub_p + " " + series
                            if len(phone) > 0:
                                phone_dict[b].append(phone)
                        phone_dict[b].append(sub_p)
                    else:
                        phone = p.replace(b + " Galaxy", "").replace("5G", "").strip()
                        if len(phone) > 0:
                            phone_dict[b].append(phone)
        elif b == "POCO":
            for p in phones:
                if p.split(" ")[0] == b:
                    phone = p.replace("5G", "").strip()
                    if len(phone) > 0:
                        phone_dict["Xiaomi"].append(phone)
        elif b == "Developer":
            for p in phones:
                if p.split(" ")[0] == b:
                    if "/" in p:
                        p_lst = p.split("/")
                        for series in p_lst[1:]:
                            sub_p = p_lst[0].replace(b, "").replace("5G", "").strip()
                            if series == "+":
                                phone = sub_p + series
                            else:
                                phone = sub_p + " " + series
                            if len(phone) > 0:
                                phone_dict[b].append(phone)
                        phone_dict[b].append(sub_p)
                    else:
                        phone = p.replace(b, "").replace("5G", "").strip()
                        if len(phone) > 0:
                            phone_dict[b].append(phone)
                        phone_dict[b].append(phone)
        else:
            for p in phones:
                if p.split(" ")[0] == b:
                    if "/" in p:
                        p_lst = p.split("/")
                        for series in p_lst[1:]:
                            sub_p = p_lst[0].replace(b, "").replace("5G", "").strip()
                            if series == "+":
                                phone = sub_p + series
                            else:
                                phone = sub_p + " " + series
                            if len(phone) > 0:
                                phone_dict[b].append(phone)
                        phone_dict[b].append(sub_p)
                    else:
                        phone = p.replace(b, "").replace("5G", "").strip()
                        if len(phone) > 0:
                            phone_dict[b].append(phone)
                        phone_dict[b].append(phone)
    phone_dict["Asus"].append("ROG Phone 2")
    phone_dict.pop("Galaxy")

    url = "https://www.theiphonewiki.com/wiki/List_of_iPhones"
    resp = requests.get(url, verify=False)
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
    phone_dict["iPhone"] = iphones

    for k in phone_dict.keys():
        phone_dict[k] = sorted(phone_dict[k], key=lambda x: len(x), reverse=True)
    
    brands = list(phone_dict.keys())
    phones = []
    for k, v in phone_dict.items():
        if k == "Samsung":
            for i in range(len(v)):
                phones.append(k+" Galaxy "+str(v[i]))
        elif k == "iPhone":
            for i in range(len(v)):
                phones.append(str(v[i]))
        else:
            for i in range(len(v)):
                phones.append(k+" "+str(v[i]))
    phones.remove("iPhone")

    return phones


class Round(Func):
    function = 'ROUND'
    arity = 2


class PttHomeView(GenericAPIView):

    queryset = Ptt.objects.all().prefetch_related("landtop")
    serializer_class = PttSerializer

    def get(self, request, *args, **krgs):
        start = time.time()
        phones = get_phones()
        fetch = (self.get_queryset()
        .values('title', 'storage')
        .annotate(old_price=Round(Avg('price', output_field=FloatField()), 0), 
                    id=Max('id', output_field=IntegerField()),
                    new_price=Min('landtop__price', output_field=IntegerField()))
        .filter(price__gte=1000, new=0, title__in=phones, created_at__gte=datetime.now()-timedelta(days=30))
        .exclude(storage__isnull=True)
        .exclude(price__isnull=True)
        .order_by('title'))

        serializer = self.serializer_class(fetch, many=True)
        data = serializer.data
        result = defaultdict(list)
        for d in data:
            if not d["new_price"]:
                d["new_price"] = "No data"
            if d["storage"]:
                d["storage"] = str(d["storage"]) + "GB"
                result[d["title"].split(" ")[0]].append(d)

        print(time.time() - start)
        return JsonResponse({"products": result}, json_dumps_params={'ensure_ascii':False})


class PttTableView(GenericAPIView):

    queryset = Ptt.objects.all().prefetch_related("landtop")
    serializer_class = PttDetailSerializer

    def get(self, request, *args, **krgs):
        title = request.GET.get('title')
        if "plus" in title:
            title = title.replace("plus", "+")
        storage = request.GET.get('storage')

        phone = "{} {}GB".format(title, storage)

        # phone_table
        fetch = (self.get_queryset()
        .filter(title=title, storage=storage, sold=0, price__gt=1000)
        .order_by('-created_at'))

        serializer = self.serializer_class(fetch, many=True)
        phone_table = serializer.data
            
        return JsonResponse({"phone": phone, "title":title, "storage": storage, "phone_table": phone_table}, json_dumps_params={'ensure_ascii':False})

class PttPriceGraphView(GenericAPIView):

    queryset = Ptt.objects.all().prefetch_related("landtop")
    serializer_class = PttDetailSerializer

    def get(self, request, *args, **krgs):
        title = request.GET.get('title')
        if "plus" in title:
            title = title.replace("plus", "+")
        storage = request.GET.get('storage')

        phone = "{} {}GB".format(title, storage)

        # phone_graph
        fetch = (self.get_queryset()
        .values(date=Cast('created_at', output_field=DateField()))
        .annotate(old_price=Round(Avg('price', output_field=FloatField()), 0), 
                  new_price=Min('landtop__price', output_field=IntegerField()),
                  min_price=Min('price'), 
                  max_price=Max('price'),
                  id=Max('id', output_field=IntegerField()))
        .filter(title=title, storage=storage, price__gt=1000)
        .exclude(storage__isnull=True)
        .exclude(price__isnull=True)
        .order_by('date'))

        serializer = PttGraphSerializer(fetch, many=True)
        phone_graph = serializer.data

        fetch = (self.get_queryset()
        .annotate(date=Cast('created_at', output_field=DateField()), 
                  avg_price_30=Round(Avg('price', output_field=FloatField()), 0))
        .filter(title=title, storage=storage, price__gt=1000, date__gt=datetime.now().date()-timedelta(days=30))
        .exclude(storage__isnull=True)
        .exclude(price__isnull=True))

        if len(fetch) > 0:
            avg_price_30 = fetch[0].avg_price_30
        else:
            avg_price_30 = 0

        phone_graph_dict = {"date": [], "old_price": [], "min_price": [], "max_price": [],
                            "new_price": [], "avg_price_30": []}
        for d in phone_graph:
            phone_graph_dict["date"].append(d["date"])
            phone_graph_dict["old_price"].append(d["old_price"])
            phone_graph_dict["min_price"].append(d["min_price"])
            phone_graph_dict["max_price"].append(d["max_price"])
            phone_graph_dict["new_price"].append(d["new_price"])
            phone_graph_dict["avg_price_30"].append(avg_price_30)
        
 
        return JsonResponse({"phone": phone, "title":title, "storage": storage, "phone_graph": phone_graph_dict}, json_dumps_params={'ensure_ascii':False})

class PttStorageGraphView(GenericAPIView):

    queryset = Ptt.objects.all().prefetch_related("landtop")
    serializer_class = PttDetailSerializer

    def get(self, request, *args, **krgs):
        title = request.GET.get('title')
        if "plus" in title:
            title = title.replace("plus", "+")
        storage = request.GET.get('storage')

        phone = "{} {}GB".format(title, storage)

        # phone graph of different storage
        fetch = (self.get_queryset()
        .values('storage', date=Cast('created_at', output_field=DateField()))
        .annotate(old_price=Round(Avg('price', output_field=FloatField()), 0), 
                  new_price=Min('landtop__price', output_field=IntegerField()),
                  min_price=Min('price'), 
                  max_price=Max('price'),
                  id=Max('id', output_field=IntegerField()))
        .filter(title=title, price__gt=1000)
        .exclude(storage__isnull=True)
        .exclude(price__isnull=True)
        .order_by('storage', 'date'))

        serializer = PttGraphSerializer(fetch, many=True)
        storage_graph = serializer.data
        storage_graph_dict = { storage_graph[0]["storage"]: defaultdict(list) }
        
        for i in range(len(storage_graph)):
            if storage_graph[i]["storage"] != storage_graph[i-1]["storage"] and i > 0:
                storage_graph_dict[ storage_graph[i]["storage"] ] = defaultdict(list)
            storage_graph_dict[ storage_graph[i]["storage"] ]["date"].append(storage_graph[i]["date"])
            storage_graph_dict[ storage_graph[i]["storage"] ]["old_price"].append(storage_graph[i]["old_price"])
            storage_graph_dict[ storage_graph[i]["storage"] ]["min_price"].append(storage_graph[i]["min_price"])
            storage_graph_dict[ storage_graph[i]["storage"] ]["max_price"].append(storage_graph[i]["max_price"])
            storage_graph_dict[ storage_graph[i]["storage"] ]["new_price"].append(storage_graph[i]["new_price"])
            
        return JsonResponse({"phone": phone, "title":title, "storage": storage, "storage_graph": storage_graph_dict}, json_dumps_params={'ensure_ascii':False})


class SaleView(GenericAPIView):
    queryset = Ptt.objects.all()

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/smartphone-smartprice/home') 
        form = SaleForm()
        context = {
        'form': form
        }
        return render(request, 'registration/sale.html', context)

    def post(self, request):
        form = SaleForm(request.POST)
        current_user = request.user
        print(form.errors)
        if form.is_valid():
            sale = form.save(commit=False)
            # default value: sold, account, created_at, source
            sale.account = current_user.username
            sale.email = current_user.email
            sale.created_at = datetime.utcnow().replace(microsecond=0) + timedelta(hours=8)

            images = []
            files = request.FILES.getlist("images")
            s3 = boto3.resource('s3', aws_access_key_id=env.AWS_ACCESS_KEY, aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY)
            s3_bucket = s3.Bucket("aws-bucket-addie")

            # create a new instance of FileSystemStorage
            fs = FileSystemStorage()
            for i in range(len(files)):
                upload_folder = "smartphone-images/"
                filename = upload_folder + current_user.username + "_" + str(int(datetime.timestamp(sale.created_at))) +f"_{i}.jpg"
                f= fs.save(filename, files[i])
                # the fileurl variable now contains the url to the file. This can be used to serve the file when needed.
                fileurl = fs.url(f)
                upload_path = str(settings.BASE_DIR) + fileurl
                s3_bucket.upload_file(upload_path, filename, ExtraArgs={'ContentType': 'image/png', 'ACL':'public-read'})
                image_url = "https://aws-bucket-addie.s3.amazonaws.com/" + filename
                images.append(image_url)

            sale.images = ",".join(images)
                
            sale.save()
            messages.success(request, 'Add Product successfully!')
        else:
            messages.error(request, 'Something went wrong. Please try again!')
        return redirect('/smartphone-smartprice/sale') 


class CommentsView(GenericAPIView):
    queryset = Ptt.objects.all()

    def get(self, request, *args, **krgs):
        title = request.GET.get('title')
        db_coll = db["sentiment"]
        fetch = [sample for sample in db_coll.find({ "title" : title })]
        doc_score = [ d["doc"]["score"] for d in fetch ]
        doc_mag = [ d["doc"]["magnitude"] for d in fetch ]
        doc = {"score": round(sum(doc_score)/len(doc_score), 2), "magnitude": round(sum(doc_mag)/len(doc_mag), 2)}
        sentences = []
        for d in fetch:
            sentences.extend(d["sentences"])

        for d in sentences:
            temp = []
            if "<" in d["content"]:
                lst = d["content"].split("<")
                for i in lst:
                    if ">" not in i:
                        temp.append(i)
                d["content"] = "，".join(temp)


        sentences = sorted([ (d["content"], d["score"], d["magnitude"]) for d in sentences 
                              if abs(d["score"]) >= 0.5 and abs(d["magnitude"]) >= 0.5 and len(d["content"]) > 5 ],
                    key=lambda x: x[1], reverse=True)
        goods = [i[0] for i in sentences if i[1] > 0]
        bads = [i[0] for i in sentences if i[1] < 0]
        arc_title = [ d["arc_title"] for d in fetch ]
        link = [ "https://www.ptt.cc/"+d["link"] for d in fetch ]
        data = {"doc":doc, "goods": goods, "bads": bads, "arc_title": arc_title, "link": link}
        
        return JsonResponse(data, json_dumps_params={'ensure_ascii':False})


class ProfileView(GenericAPIView):

    queryset = Ptt.objects.all()
    serializer_class = ProfileSerializer

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/smartphone-smartprice/login')
        current_user = request.user
        fetch = self.queryset.all().filter(account=current_user.username, source="native")
        serializer = self.serializer_class(fetch, many=True)
        sale_post = serializer.data
        username = current_user.username
        email = current_user.email
        data = {"user_info": {"username": username, "email": email},
                "sale_post": sale_post}
        return JsonResponse(data, json_dumps_params={'ensure_ascii':False}, safe=False)

