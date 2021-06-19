import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from datetime import datetime
import re
from collections import defaultdict
import time
import json

from crawler_model import Landtop
from util import make_phone_dict

ua = UserAgent()
fakeua = ua.random


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