from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, QueryDict
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from bs4 import BeautifulSoup
from django.db.models import Count, FloatField, IntegerField, DateField, Avg, Max, Func, F, Min
from django.db.models.functions import Cast
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from ratelimit.decorators import ratelimit
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
from .util import get_phones
import env

PRICE_FLOOR = 1000
PRICE_CEIL = 99999
PRICE_DAYS_PERIOD = 30
IS_NOT_NEW = 0
IS_NOT_SOLD = 0
UTC_8 = 8
SENTIMENT_SCALAR = 20

# pages

@ratelimit(key='ip', rate='2/m')
def home_page(request):
    return render(request, 'home.html')


def detail_page(request, title, storage):
    return render(request, 'detail.html')


class ProfilePageView(GenericAPIView):
    queryset = Ptt.objects.all()
    serializer_class = PttSerializer

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login') 
        return render(request, 'profile.html')

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        id = request.POST.get('id')
        Ptt.objects.filter(id=id).update(sold=True)
        return redirect('profile')


class SignUpView(GenericAPIView):
    queryset = User.objects.all()

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home') 
        form = SignUpForm()
        context = {
        'form': form
        }
        return render(request, 'registration/signup.html', context)
    
    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.save()
            auth_login(request, user)
            return redirect('home')
        else:
            if form.errors:
                messages.error(request, form.errors)
            else:
                messages.error(request, '操作有誤！請再試一次。')
        return redirect('signup') 


class LoginView(GenericAPIView):
    queryset = User.objects.all()

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home') 
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
            return redirect('home')  #重新導向到首頁
        else:
            messages.error(request, '帳號或密碼錯誤')
        return redirect('login') 


class LogoutView(GenericAPIView):
    queryset = User.objects.all()

    def get(self, request):
        if request.user.is_authenticated:
            auth_logout(request)
        return redirect('login')


class PostView(GenericAPIView):
    queryset = Ptt.objects.all()
    serializer_class = ProfileSerializer

    def get(self, request, id):
        id = request.path.split('/')[-1]
        fetch = get_object_or_404(Ptt, pk=id)
        serializer = self.serializer_class(fetch)
        data = serializer.data
        data["images"] = data["images"].split(",")
        context = {
        'data': data
        }
        return render(request, 'post.html', context)


ssl_file = env.SSL_FILE
def get_ssl_file(request):
    file = open(ssl_file).read()
    return HttpResponse(file)
    

# APIs

class Round(Func):
    function = 'ROUND'
    arity = 2


class PttHomeView(GenericAPIView):
    queryset = Ptt.objects.all().prefetch_related("landtop")
    serializer_class = PttSerializer

    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **krgs):
        phones = get_phones()
        fetch = (self.get_queryset()
        .values('title', 
                'storage')
        .annotate(old_price=Round(Avg('price', output_field=FloatField()), 0), 
                  id=Max('id', output_field=IntegerField()),
                  new_price=Min('landtop__price', 
                  output_field=IntegerField()))
        .filter(price__gte=PRICE_FLOOR, 
                new=IS_NOT_NEW, 
                title__in=phones, 
                created_at__gte=datetime.now()-timedelta(days=PRICE_DAYS_PERIOD))
        .exclude(storage__isnull=True)
        .exclude(price__isnull=True)
        .order_by('title'))

        serializer = self.serializer_class(fetch, many=True)
        phones = serializer.data
        result = defaultdict(list)
        for phone in phones:
            if not phone["new_price"]:
                phone["new_price"] = "No data"
            if phone["storage"]:
                phone["storage"] = str(phone["storage"]) + "GB"
                result[phone["title"].split(" ")[0]].append(phone)

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
        .filter(title=title, 
                storage=storage, 
                sold=IS_NOT_SOLD, 
                price__gte=PRICE_FLOOR, 
                price__lt=PRICE_CEIL)
        .exclude(storage__isnull=True)
        .exclude(price__isnull=True)
        .order_by('-created_at'))

        serializer = self.serializer_class(fetch, many=True)
        phone_table = serializer.data
            
        return JsonResponse({"phone": phone, "title":title, "storage": storage, "phone_table": phone_table}, 
                             json_dumps_params={'ensure_ascii':False})


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
        .filter(title=title, 
                storage=storage, 
                price__gte=PRICE_FLOOR, 
                price__lt=PRICE_CEIL)
        .exclude(storage__isnull=True)
        .exclude(price__isnull=True)
        .order_by('date'))

        serializer = PttGraphSerializer(fetch, many=True)
        phone_graph = serializer.data

        fetch = (self.get_queryset()
        .annotate(date=Cast('created_at', output_field=DateField()), 
                  avg_price_30=Round(Avg('price', output_field=FloatField()), 0))
        .filter(title=title, 
                storage=storage, 
                price__gte=PRICE_FLOOR, 
                date__gte=datetime.now().date()-timedelta(days=PRICE_DAYS_PERIOD), 
                price__lt=PRICE_CEIL)
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
        
 
        return JsonResponse({"phone": phone, "title":title, "storage": storage, "phone_graph": phone_graph_dict}, 
                             json_dumps_params={'ensure_ascii':False})


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
        .values('storage', 
                date=Cast('created_at', output_field=DateField()))
        .annotate(old_price=Round(Avg('price', output_field=FloatField()), 0), 
                  new_price=Min('landtop__price', output_field=IntegerField()), 
                  min_price=Min('price'), 
                  max_price=Max('price'), 
                  id=Max('id', output_field=IntegerField()))
        .filter(title=title, price__gte=PRICE_FLOOR, price__lt=PRICE_CEIL)
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
            
        return JsonResponse({"phone": phone, "title":title, "storage": storage, "storage_graph": storage_graph_dict}, 
                             json_dumps_params={'ensure_ascii':False})


class SaleView(GenericAPIView):
    queryset = Ptt.objects.all()

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('home') 
        form = SaleForm()
        context = {
            'form': form
            }
        return render(request, 'sale.html', context)

    def post(self, request):
        form = SaleForm(request.POST, request.FILES)
        current_user = request.user
        if form.is_valid():
            sale = form.save(commit=False)

            # default value: sold, account, created_at, source
            sale.account = current_user.username
            sale.email = current_user.email
            sale.created_at = datetime.utcnow().replace(microsecond=0) + timedelta(hours=UTC_8)

            # images
            images = []
            files = request.FILES.getlist("images")
            s3 = boto3.resource('s3', aws_access_key_id=env.AWS_ACCESS_KEY, aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY)
            s3_bucket = s3.Bucket("aws-bucket-addie")

            # create a new instance of FileSystemStorage
            fs = FileSystemStorage()
            for i in range(len(files)):
                upload_folder = "smartphone-images/"
                filename = upload_folder + current_user.username + "_" + str(int(datetime.timestamp(sale.created_at))) + f"_{i}.jpg"
                f = fs.save(filename, files[i])

                fileurl = fs.url(f)
                upload_path = str(settings.BASE_DIR) + fileurl
                s3_bucket.upload_file(upload_path, filename, 
                                      ExtraArgs={'ContentType': 'image/png', 'ACL':'public-read'})
                image_url = "https://aws-bucket-addie.s3.amazonaws.com/" + filename
                images.append(image_url)
                os.system(f'rm -rf {upload_path}')

            sale.images = ",".join(images)
                
            sale.save()
            messages.success(request, '上架商品成功')
        else:
            if form.errors:
                messages.error(request, form.errors)
            else:
                messages.error(request, '喔嗚，出錯了，請再試一次。')
        return redirect('sale') 


class CommentsView(GenericAPIView):
    queryset = Ptt.objects.all()

    def get(self, request, *args, **krgs):
        title = request.GET.get('title')
        db_coll = db["sentiment"]
        max_score = db_coll.find_one(sort=[("doc.score", -1)])["doc"]["score"]
        fetch = [ sample for sample in db_coll.find({"title" : title}) ]
        if len(fetch) > 0:
            doc_score = [ d["doc"]["score"] for d in fetch ]
            doc_mag = [ d["doc"]["magnitude"] for d in fetch ]
            doc = {"score": round( (sum(doc_score)/len(doc_score)) / max_score, 2 ), 
                   "magnitude": round(sum(doc_mag)/len(doc_mag), 2)}

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


            sentences = sorted([{"content": d["content"], "score": d["score"], "magnitude": d["magnitude"]} 
                                for d in sentences 
                                if abs(d["score"]) >= 0.5 and abs(d["magnitude"]) >= 0.5 and len(d["content"]) > 5], 
                               key=lambda x: x["score"], 
                               reverse=True)
            goods = [sentence["content"] for sentence in sentences if sentence["score"] > 0]
            bads = [sentence["content"] for sentence in sentences if sentence["score"] < 0]
            arc_title = [ d["arc_title"] for d in fetch ]
            link = [ "https://www.ptt.cc/" + d["link"] for d in fetch ]
            data = {"doc":doc, "goods": goods, "bads": bads, "arc_title": arc_title, "link": link}
        else:
            data = {}
            
        return JsonResponse(data, json_dumps_params={'ensure_ascii':False})


class ProfileView(GenericAPIView):
    queryset = Ptt.objects.all()
    serializer_class = ProfileSerializer

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        current_user = request.user
        fetch = self.queryset.all().filter(account=current_user.username, source="native")
        serializer = self.serializer_class(fetch, many=True)
        sale_post = serializer.data
        username = current_user.username
        email = current_user.email
        data = {"user_info": {"username": username, "email": email},
                "sale_post": sale_post}
        return JsonResponse(data, json_dumps_params={'ensure_ascii':False}, safe=False)