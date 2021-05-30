import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from google.cloud import language_v1
from pymongo import MongoClient
from dotenv import load_dotenv

from datetime import datetime
import re
from collections import defaultdict
import json
import pprint
import os

load_dotenv()
user = os.getenv("MONGO_USER")
psw = os.getenv("MONGO_PSW")
host = os.getenv("MONGO_HOST")

ua = UserAgent()
fakeua = ua.random

uri = "mongodb://{user}:{psw}@{host}:27017".format(user=user, psw=psw, host=host)
client = MongoClient(uri)
db = client["mobileComm"]
db_coll = db["sentiment"]

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
    extend = ["note20ultra", "s20ultra", "s21ultra", "s20+", "s21+", "s20", "s21"]
    for s in extend:
        phone_list.append(s)

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
    phone_list = sorted(list(phone_set))
    phone_list.remove("Asus ROG Phone II")
    return phone_list

def sample_analyze_sentiment(text_content):
    """
    Analyzing Sentiment in a String

    Args:
      text_content The text content to analyze
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= os.path.join(os.path.expanduser("~"), "smartphone-smartprice-key.json")

    client = language_v1.LanguageServiceClient()

    type_ = language_v1.Document.Type.PLAIN_TEXT

    document = {"content": text_content, "type_": type_}

    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_sentiment(request = {'document': document, 'encoding_type': encoding_type})

    doc = {}
    doc["score"] = response.document_sentiment.score
    doc["magnitude"] = response.document_sentiment.magnitude

    # Get sentiment for all sentences in the document
    sentences = []
    for sentence in response.sentences:
        d = {}
        d["content"] = sentence.text.content.replace(".", "").replace("。", "")
        d["score"] = sentence.sentiment.score
        d["magnitude"] = sentence.sentiment.magnitude
        sentences.append(d)
    
    return doc, sentences

def crawl_comm(links):
    data = []
    for link in links:
        url = "https://www.ptt.cc" + link[2]
        ua = UserAgent()
        fakeua = ua.random
        headers = {"Origin": "https://www.ptt.cc",
                "Referer": "https://fonts.googleapis.com/",
                "sec-ch-ua-mobile": "?0",
                "User-Agent": fakeua}
        resp = requests.get(url, headers=headers)
        if "200" in str(resp):
            soup = BeautifulSoup(resp.text, "html.parser")
            main = soup.find("div", id="main-content")
            if "※ 引述" in str(main):   
                body = str(main).split('※ 引述')[0].split('</span></div>')[-1].replace(" ","").replace("\n", "。")
            else:
                body = str(main).split('--')[0].split('</span></div>')[-1].replace(" ","").replace("\n", "。")
        doc, sentences = sample_analyze_sentiment(body)
        d = {"title": link[0], "arc_title": link[1], "link": link[2], "page": link[3], "doc": doc, "sentences": sentences}
        data.append(d)
    return data

def crawl_comm_pages():
    
    for page in range(1, 100):

        ua = UserAgent()
        fakeua = ua.random
        headers = {"Origin": "https://www.ptt.cc",
                "Referer": "https://fonts.googleapis.com/",
                "sec-ch-ua-mobile": "?0",
                "User-Agent": fakeua}

        url = "https://www.ptt.cc/bbs/MobileComm/search?page={}&q=%E5%BF%83%E5%BE%97".format(page)
        print(url)
        phone_list = get_phones()
        resp = requests.get(url, headers=headers)
        index_soup = BeautifulSoup(resp.text, "html.parser")
        keywords = ["換", "vs", "v.s", "vs.", "v.s."]
        title = index_soup.findAll("div", class_="title")

        links = []
        for t in title:
            if any(keyword in t.text for keyword in keywords):
                pass
            else:
                for p in phone_list:
                    if p.replace(" ", "").lower() in t.text.replace(" ", "").lower():
                        print(p, t)
                        links.append( (p, t.text.strip(), t.find("a")["href"], page) )
                        break
                        break
        
        data = crawl_comm(links)
        if len(data) > 0:
            db_coll.insert_many(data)
        
if __name__ == '__main__':
    crawl_comm_pages()