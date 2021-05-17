import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from datetime import datetime
import re
from collections import defaultdict
import time
import json

from crawler_model import Landtop

ua = UserAgent()
fakeua = ua.random

def make_phone_dict():
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
                            print(phone)
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
    for k in phone_dict.keys():
        phone_dict[k] = sorted(phone_dict[k], key=lambda x: len(x), reverse=True)

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
    iphones = sorted(iphones, reverse=True)
    phone_dict["iPhone"] = iphones
    return phone_dict

def get_landtop_phones(phone_dict):
    url = "https://www.landtop.com.tw/product_categories/phones"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    phones = soup.find_all("div", class_="product-list")
    data = []
    for i in range(len(phones)):
        title = phones[i].select("div div div a h2")[0].text
        price = phones[i].find("div", class_="special-price").select("div span")[1].text.strip().replace(",", "")

        try:
            price = int(price)
        except:
            continue

        if "Apple" in title:
            title = title.replace("Apple", "").strip()
        elif "Google" in title:
            title = title.replace("Google", "").strip()
        elif "realme" in title:
            title = title.replace("realme ", "").strip()
        elif "小米 紅米" in title:
            title = "Redmi " + title.replace("小米 紅米 ", "").strip()
        elif "小米 小米" in title:
            title = "Xiaomi mi " + title.replace("小米 小米", "").strip()
        elif "小米" in title:
            title = "Xiaomi " + title.replace("小米 ", "").strip()

        if (title.split(" ")[0] not in list(phone_dict.keys())) or ("Tab" in title) or ("iPad" in title):
            continue

        for k in phone_dict.keys():
            if k.lower() in title.lower().replace(" ", ""): 
                for phone in phone_dict[k]:
                    if phone.lower().replace(" ", "") in title.lower().replace(" ", ""):
                        for s in  ["32", "64", "128", "256", "512"]:
                            if s in title:
                                storage = int(s)
                                break
                        if k == "Samsung":
                            title = k + " " + "Galaxy" + " " + phone
                        elif k == "iPhone":
                            title = phone
                        else:
                            title = k + " " + phone
                        break
                break
        data.append([ title, storage , price, datetime.now().date() ])
    return data

if __name__ == '__main__':
    phone_dict = make_phone_dict()
    landtop_phones = get_landtop_phones(phone_dict)
    db = Landtop()
    db.insert_landtop_phones(landtop_phones)