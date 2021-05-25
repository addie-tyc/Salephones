from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.generics import GenericAPIView
from bs4 import BeautifulSoup

from datetime import datetime, timedelta
import requests
from collections import defaultdict
import time

from smartphone_app.models import Ptt, Landtop
from smartphone_app.serializers import PttSerializer, LandtopSerializer, PttDetailSerializer, PttGraphSerializer
from django.db.models import Count, FloatField, IntegerField, DateField, Avg, Max, Func, F, Min
from django.db.models.functions import Cast


def home_page(request):
    return render(request, 'home_page.html')

def detail_page(request, title, storage):
    return render(request, 'detail_page.html')

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
        brand = request.GET.get('brand')
        phones = get_phones()
        if brand:
            fetch = (self.get_queryset()
            .values('title', 'storage')
            .annotate(old_price=Round(Avg('price', output_field=FloatField()), 0), 
                      id=Max('id', output_field=IntegerField()))
            .filter(price__gte=1000, new=0, title__in=phones, title__startswith=brand, created_at__gte=datetime.now()-timedelta(days=30))
            .exclude(storage__isnull=True, price__isnull=True)
            .order_by('title'))
        else:
            fetch = (self.get_queryset()
            .values('title', 'storage')
            .annotate(old_price=Round(Avg('price', output_field=FloatField()), 0), 
                      id=Max('id', output_field=IntegerField()),
                      new_price=Min('landtop__price', output_field=IntegerField()))
            .filter(price__gte=1000, new=0, title__in=phones, created_at__gte=datetime.now()-timedelta(days=30))
            .exclude(storage__isnull=True, price__isnull=True)
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


class PttDetailView(GenericAPIView):

    queryset = Ptt.objects.all().prefetch_related("landtop")
    serializer_class = PttDetailSerializer

    def get(self, request, *args, **krgs):
        title = request.GET.get('title')
        if "plus" in title:
            title = title.replace("plus", "+")
        storage = request.GET.get('storage')

        phone = "{} {}GB".format(title, storage)

        fetch = (self.get_queryset()
        .filter(title=title, storage=storage, sold=0, price__gt=1000)
        .order_by('-created_at'))

        serializer = self.serializer_class(fetch, many=True)
        phone_table = serializer.data


        fetch = (self.get_queryset()
        .values(date=Cast('created_at', output_field=DateField()))
        .annotate(old_price=Round(Avg('price', output_field=FloatField()), 0), 
                  new_price=Min('landtop__price', output_field=IntegerField()),
                  min_price=Min('price'), 
                  max_price=Max('price'),
                  id=Max('id', output_field=IntegerField()))
        .filter(title=title, storage=storage, price__gt=1000)
        .exclude(storage__isnull=True, price__isnull=True)
        .order_by('date'))

        serializer = PttGraphSerializer(fetch, many=True)
        phone_graph = serializer.data


        fetch = (self.get_queryset()
        .annotate(date=Cast('created_at', output_field=DateField()), 
                  avg_price_30=Round(Avg('price', output_field=FloatField()), 0))
        .filter(title=title, storage=storage, price__gt=1000, date__gt=datetime.now().date()-timedelta(days=30))
        .exclude(storage__isnull=True, price__isnull=True))


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
            
        return JsonResponse({"phone": phone, "phone_table": phone_table, "phone_graph": phone_graph_dict}, json_dumps_params={'ensure_ascii':False})
