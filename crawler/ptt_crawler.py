import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from datetime import datetime
import re
from collections import defaultdict
import time
import json

from crawler_model import Ptt

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
    while "ROG Phone II" in phone_dict["Asus"]:
        phone_dict["Asus"].remove("ROG Phone II")

    phone_dict.pop("Galaxy")

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
    phone_dict["iPhone"] = iphones

    for k in phone_dict.keys():
        phone_dict[k] = sorted(phone_dict[k], key=lambda x: len(x), reverse=True)

    return phone_dict

def read_phone_catalog():
    with open('phone_catalog.json', 'r') as fp:
        phone_dict = json.load(fp)
    return phone_dict

def make_iphone_matches(phone_dict):
    phone_brand_set = set()
    for k in phone_dict.keys():
        for v in phone_dict[k]:
            for iphone in [ i.replace("iPhone", "").strip() for i in phone_dict["iPhone"] ]:
                if v == iphone:
                    phone_brand_set.add(v)
    iphone_matches = sorted([v for v in list(set([ i.replace("iPhone", "").strip() for i in phone_dict["iPhone"] ]) - phone_brand_set) if len(v) > 0], key=lambda x: len(x), reverse=True)
    iphone_matches = [ i for i in iphone_matches if ("11" in i) or ("12" in i) or ("SE2" in i)]
    iphone_matches.remove("12")
    iphone_matches.remove("11")
    return iphone_matches

def get_last_page(source):
    ua = UserAgent()
    fakeua = ua.random
    headers = {"Origin": "https://www.ptt.cc",
            "Referer": "https://fonts.googleapis.com/",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": fakeua}
    url = "https://www.ptt.cc/bbs/{}/index.html".format(source)
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    previous = soup.find_all("a", class_="btn wide")[1]["href"]
    previous_page_num = int(re.findall(r"\d+", previous)[0])
    return previous_page_num

def crawl_mobilesales(links, page, sold, phone_dict, raw_data, data, error_links):
    for link in links:
        url = "https://www.ptt.cc" + link
        # print(url)
        # GET request from url and parse via BeautifulSoup
        ua = UserAgent()
        fakeua = ua.random
        headers = {"Origin": "https://www.ptt.cc",
                "Referer": "https://fonts.googleapis.com/",
                "sec-ch-ua-mobile": "?0",
                "User-Agent": fakeua}
        resp = requests.get(url, headers=headers)
        if "200" in str(resp):
            try:
                soup = BeautifulSoup(resp.text, "html.parser")

                # basic info: accout, board, title, created_at
                info = [ i.text.strip() for i in soup.findAll("span", class_="article-meta-value")]
                try:
                    title = re.findall(r'售物品.+\n', str(soup.find("div", id="main-content")))[0][4:].strip()      
                    
                    if len(title) == 0:
                        title = info[2]     

                except IndexError:
                    title = info[2]

                if ("小米" in title.lower()) or ("redmi" in title.lower()) or ("poco" in title.lower()):
                    title = "Xiaomi" + " " + title
                if ("紅米" in title.lower()):
                    title = "Redmi" + " " + title
                if ("三星" in title.lower()) and ("samsung" in title.lower()):
                    title = "Samsung" + " " + title
                if ("zenfone" in title.lower()) and ("asus" not in title.lower()):
                    title = "Asus" + " " + title

                title = " ".join(re.findall(r"[a-zA-Z0-9+]+", title))
                storage = None
                if "rog" in title.lower():
                    for phone in phone_dict["Asus"]:
                        if phone.lower().replace(" ", "") in title.lower().replace(" ", ""):
                            for s in  ["32", "64", "128", "256", "512"]:
                                if s in title:
                                    storage = int(s)
                                    break
                            title = "Asus" + " " + phone
                            break

                samsung_matches = ["note20ultra", "s20ultra", "s21ultra"]
                if any(x in title.lower().replace(" ", "") for x in samsung_matches):
                    for phone in phone_dict["Samsung"]:
                        if phone.lower().replace(" ", "") in title.lower().replace(" ", ""):
                            for s in  ["32", "64", "128", "256", "512"]:
                                if s in title:
                                        storage = int(s)
                                        break
                            title = "Samsung Galaxy" + " " + phone
                            break

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

                if title.split(" ")[0] in phone_dict.keys():
                    pass
                else:
                    for x in iphone_matches:
                        if x.lower().replace(" ", "") in title.lower().replace(" ", ""):
                            print(x)
                            for phone in phone_dict["iPhone"]:
                                if x == phone.lower().replace(" ", ""):
                                    for s in  ["32", "64", "128", "256", "512"]:
                                        if s in title:
                                            storage = int(s)
                                            break
                                    title = phone
                                    print("iPhone:", title)
                                    break
                            break

                try:
                    account = info[0]
                    created_at = datetime.strptime(info[3][3:].strip(), '%b %d %H:%M:%S %Y')
                except IndexError:
                    account = None
                    created_at = " ".join(re.findall(r'時間.+\n', str(soup.find("div", id="main-content")))[0].split(" ")[2:]).strip()
                    created_at = datetime.strptime(created_at, '%b %d %H:%M:%S %Y')


                # status
                try:
                    # status = re.findall(r'物品狀況.+\n', str(soup.find("div", id="main-content")))[0].strip()
                    # if len(status) <= 5:
                    #     status = re.findall(r'狀況.+盒裝內含', str(soup.find("div", id="main-content")).replace("\n", ""))[0]

                    if ("全新" in info[2]):
                        new = True
                    elif ("近全新" in info[2]) or ("外觀全新" in info[2]) or ("全新耳機" in info[2]) or ("全新配件" in info[2]):
                        new = False
                    else:
                        new = False
                except IndexError:
                    new = False

                # price
                try:
                    wording = "價格"
                    price = re.findall(r'售價格.+\n', str(soup.find("div", id="main-content")))
                    if len(price) == 0:
                        wording = "金額"
                        price = re.findall(r'售金額.+\n', str(soup.find("div", id="main-content")))
                    price = price[0].strip().replace(",", "")
                    price = int(re.search(r'\d+', price).group())
                except IndexError:
                    if wording == "金額":
                        price = re.findall(r'售金額.+', str(soup.find("div", id="main-content")).replace("\n", "").replace(",", "").replace(" ", ""))
                        price = int(re.findall(r'\d+', price)[0])
                    else:
                        price = re.findall(r'售價格.+', str(soup.find("div", id="main-content")).replace("\n", "").replace(",", "").replace(" ", ""))[0].strip()
                        price = int(re.findall(r'\d+', price)[0])
                except AttributeError:
                    sold = True
                    price = None
                
                # items included
                try:
                    box = re.findall(r'盒裝.+\n', str(soup.find("div", id="main-content")))[0].strip()
                    if len(box) <= 5:
                        box = re.findall(r'盒裝內含.+購買', str(soup.find("div", id="main-content")).replace("\n", ""))[0]
                        box = box.replace(" ", "")[:-2]
                except IndexError:
                    box = None

                data.append([title, storage, price, new, sold, account, box, url, created_at, page, "mobilesales"])
                raw_data.append([url, str(soup.find("body"))])
            except:
                error_links.append(url)

def crawl_macshop(links, page, sold, iphones, raw_data, data, error_links):
    for link in links:
        url = "https://www.ptt.cc" + link
        # GET request from url and parse via BeautifulSoup
        ua = UserAgent()
        fakeua = ua.random
        headers = {"Origin": "https://www.ptt.cc",
                "Referer": "https://fonts.googleapis.com/",
                "sec-ch-ua-mobile": "?0",
                "User-Agent": fakeua}
        resp = requests.get(url, headers=headers)
        if "200" in str(resp):
            try:
                soup = BeautifulSoup(resp.text, "html.parser")

                # basic info: accout, board, title, created_at
                info = [ i.text.strip() for i in soup.findAll("span", class_="article-meta-value")]
                try:
                    spec = re.findall(r'規格.+\n', str(soup.find("div", id="main-content")))[0].strip()
                except:
                    spec = ""
                try:
                    title = info[2]

                    if len(title) == 0:
                        title = info[2]     
                except IndexError:
                    title = re.findall(r'型號.+\n', str(soup.find("div", id="main-content")))[0][2:].strip()

                title = " ".join(re.findall(r"[a-zA-Z0-9+]+", title))
                storage = None

                for iphone in iphones:
                    if iphone.lower().replace(" ", "") in title.lower().replace(" ", ""): 
                        for s in  ["32", "64", "128", "256", "512"]:
                            if (s in title) or (s in spec):
                                storage = int(s)
                                break
                        title = iphone
                        break

                if "iPhone" in title:
                    pass
                else:
                    for x in iphone_matches:
                        if x.lower().replace(" ", "") in title.lower().replace(" ", ""):
                            for iphone in iphones:
                                if x == iphone.lower().replace(" ", ""):
                                    for s in  ["32", "64", "128", "256", "512"]:
                                        if (s in title) or (s in spec):
                                            storage = int(s)
                                            break
                                    title = iphone
                                    break
                            break

                try:
                    account = info[0]
                    created_at = datetime.strptime(info[3][3:].strip(), '%b %d %H:%M:%S %Y')
                except IndexError:
                    account = None
                    created_at = " ".join(re.findall(r'時間.+\n', str(soup.find("div", id="main-content")))[0].split(" ")[2:]).strip()
                    created_at = datetime.strptime(created_at, '%b %d %H:%M:%S %Y')

                # status
                try:
                    status = re.findall(r'型號.+\n', str(soup.find("div", id="main-content")))[0].strip()
                    if len(status) <= 5:
                        status = re.findall(r'型號.+規格', str(soup.find("div", id="main-content")).replace("\n", ""))[0]

                    if ("全新" in info[2]) or ("全新" in status):
                        new = True
                    elif ("近全新" in info[2]) or ("近全新" in status) or ("外觀全新" in status) or ("全新配件" in status) or ("全新耳機" in status):
                        new = False
                    else:
                        new = False
                except IndexError:
                    new = False

                # price
                try:
                    price = re.findall(r'售價.+\n', str(soup.find("div", id="main-content")))
                    price = price[0].strip().replace(",", "")
                    price = int(re.search(r'\d+', price).group())
                except AttributeError:
                    try:
                        price = re.findall(r'售價.+', str(soup.find("div", id="main-content")).replace("\n", "").replace(",", "").replace(" ", ""))[0].strip()
                        price = int(re.search(r'\d+', price).group())
                    except AttributeError:
                        price = None
                
                # items included
                try:
                    box = re.findall(r'盒裝.+\n', str(soup.find("div", id="main-content")))[0].strip()
                    if len(box) <= 5:
                        box = re.findall(r'盒裝配件.+售價', str(soup.find("div", id="main-content")).replace("\n", ""))[0]
                        box = box.replace(" ", "")[:-2]
                except IndexError:
                    box = None

                data.append([title, storage, price, new, sold, account, box, url, created_at, page, "MacShop"])
                raw_data.append([url, str(soup.find("body"))])
            except:
                error_links.append(url)
                raw_data.append([url, str(soup.find("body"))])

def main_mobilesales(last_page, max_page, phone_dict):
    raw_data = []
    data = []
    error_links = []
    init = time.time()
    for page in range(last_page, max_page, -1):
        start = time.time()
        ua = UserAgent()
        fakeua = ua.random
        headers = {"Origin": "https://www.ptt.cc",
                "Referer": "https://fonts.googleapis.com/",
                "sec-ch-ua-mobile": "?0",
                "User-Agent": fakeua}

        url = "https://www.ptt.cc/bbs/mobilesales/index{}.html".format(page)
        print(url)
        # GET request from url and parse via BeautifulSoup
        resp = requests.get(url, headers=headers)
        #resp.encoding = 'utf-8' # encoded with format utf-8 for chinese character
        index_soup = BeautifulSoup(resp.text, "html.parser")
        title = index_soup.findAll("div", class_="title")
        links = [ t.find("a")["href"] for t in title if ("賣" in str(t)) and ("已售" not in str(t)) and ("售出" not in str(t))]
        sold_links = [ t.find("a")["href"] for t in title if ("已售" in str(t)) or ("售出" in str(t))]

        crawl_mobilesales(links, page, False, phone_dict, raw_data, data, error_links)
        crawl_mobilesales(sold_links, page, True, phone_dict, raw_data, data, error_links)
        print(time.time()-start, time.time()-init)
        if page%100 == 0:
            db = Ptt()
            db.insert_post(raw_data, data)
            print("Insert {} Success.".format(page))
            raw_data = []
            data = []
    db = Ptt()
    db.insert_post(raw_data, data)
    raw_data = []
    data = []
    print(len(error_links))
    print(error_links)

def main_macshop(last_page, max_page, phone_dict):
    raw_data = []
    data = []
    error_links = []
    init = time.time()
    for page in range(last_page, max_page, -1):
        start = time.time()
        ua = UserAgent()
        fakeua = ua.random
        headers = {"Origin": "https://www.ptt.cc",
                "Referer": "https://fonts.googleapis.com/",
                "sec-ch-ua-mobile": "?0",
                "User-Agent": fakeua}

        url = "https://www.ptt.cc/bbs/mobilesales/index{}.html".format(page)
        print(url)
        # GET request from url and parse via BeautifulSoup
        resp = requests.get(url, headers=headers)
        #resp.encoding = 'utf-8' # encoded with format utf-8 for chinese character
        index_soup = BeautifulSoup(resp.text, "html.parser")
        title = index_soup.findAll("div", class_="title")
        links = [ t.find("a")["href"] for t in title if ("販售" in str(t)) and ("已售" not in str(t)) and ("售出" not in str(t)) and ("iPhone" in str(t))]
        sold_links = [ t.find("a")["href"] for t in title if (("已售" in str(t)) or ("售出" in str(t))) and ("iPhone" in str(t))]

        crawl_macshop(links, page, False, phone_dict, raw_data, data, error_links)
        crawl_macshop(sold_links, page, True, phone_dict, raw_data, data, error_links)
        print(time.time()-start, time.time()-init)
        if page%100 == 0:
            db = Ptt()
            db.insert_post(raw_data, data)
            print("Insert {} Success.".format(page))
            raw_data = []
            data = []
    db = Ptt()
    db.insert_post(raw_data, data)
    raw_data = []
    data = []
    print(len(error_links))
    print(error_links)

if __name__ == '__main__':
    phone_dict = make_phone_dict()
    iphone_matches = make_iphone_matches(phone_dict)
    last_page = get_last_page("mobilesales")
    max_page = Ptt().select_max_page_number("mobilesales") or 20300
    main_mobilesales(last_page, max_page, phone_dict)

    last_page = get_last_page("MacShop")
    max_page = Ptt().select_max_page_number("MacShop") or 18900
    main_macshop(last_page, max_page, phone_dict["iPhone"])

# airflow users create \
#     --username admin \
#     --firstname addie \
#     --lastname chung \
#     --role Admin \
#     --email addiechung.tyc@gmail.com
