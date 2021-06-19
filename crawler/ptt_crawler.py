import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from datetime import datetime
import re
from collections import defaultdict
import time
import json

from crawler_model import Ptt
from util import make_phone_dict, make_iphone_matches

ua = UserAgent()
fakeua = ua.random


def get_ptt_last_page(source):
    headers = {"Origin": "https://www.ptt.cc",
            "Referer": "https://fonts.googleapis.com/",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"}
    url = "https://www.ptt.cc/bbs/{}/index.html".format(source)
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    previous = soup.find_all("a", class_="btn wide")[1]["href"]
    ptt_last_page = int(re.findall(r"\d+", previous)[0])+1
    return ptt_last_page


def get_db_last_page(source):
    sql_hook = MySqlHook(mysql_conn_id="RDS-smartphone")
    conn = sql_hook.get_conn()
    conn.ping()
    cur = conn.cursor()
    cur.execute('''
                    SELECT MAX(page_number) AS last_page_in_db FROM ptt
                     WHERE source = %s
                    ''', (source,))
    db_last_page = int(cur.fetchone()[0])-1
    return db_last_page


def get_mobilesales_link(ptt_last_page, db_last_page):
    links = []
    for page in range(ptt_last_page, db_last_page, -1):
        headers = {"Origin": "https://www.ptt.cc",
                "Referer": "https://fonts.googleapis.com/",
                "sec-ch-ua-mobile": "?0",
                "User-Agent": "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"}

        url = "https://www.ptt.cc/bbs/mobilesales/index{}.html".format(page)
        resp = requests.get(url, headers=headers)

        index_soup = BeautifulSoup(resp.text, "html.parser")
        title = index_soup.findAll("div", class_="title")
        links.extend([ (page, t.find("a")["href"]) for t in title if ("賣" in str(t))])
    return links


def crawl_mobilesales(links, phone_dict):
    raw_data = []
    data = []
    for link in links:
        url = "https://www.ptt.cc" + link[1]
        sold = False
        print(url)
        # GET request from url and parse via BeautifulSoup
        headers = {"Origin": "https://www.ptt.cc",
                "Referer": "https://fonts.googleapis.com/",
                "sec-ch-ua-mobile": "?0",
                "User-Agent": "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"}
        resp = requests.get(url, headers=headers)
        if "200" in str(resp):
            try:
                soup = BeautifulSoup(resp.text, "html.parser")
                body = soup.find("body")
                if "已售" in str(body) or "售出" in str(body):
                    sold = True
                    
                # basic info: accout, board, title, created_at
                info = [ i.text.strip() for i in soup.findAll("span", class_="article-meta-value")]
                try:
                    title = re.findall(r'售物品.+\n', str(soup.find("div", id="main-content")))[0][4:].strip()      
                    
                    if len(title) == 0:
                        title = info[2]     

                except IndexError:
                    title = info[2]

                if ("紅米" in title.lower()) or ("redmi" in title.lower()):
                    title = "Redmi" + " " + title
                elif ("小米" in title.lower()) or ("poco" in title.lower()):
                    title = "Xiaomi" + " " + title
                elif ("三星" in title.lower()) and ("samsung" in title.lower()):
                    title = "Samsung" + " " + title
                elif ("zenfone" in title.lower()) and ("asus" not in title.lower()):
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
                            for phone in phone_dict["iPhone"]:
                                if x == phone.lower().replace(" ", ""):
                                    for s in  ["32", "64", "128", "256", "512"]:
                                        if s in title:
                                            storage = int(s)
                                            break
                                    title = phone
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
                if price:
                    if price > 999:
                        data.append([title, storage, price, new, sold, account, box, url, created_at, link[0], "mobilesales"])
                        raw_data.append([url, str(soup.find("body"))]) 
            except:
                raw_data.append([url, str(soup.find("body"))])
    return raw_data, data 


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


def main_macshop(ptt_last_page, db_last_page, phone_dict):
    raw_data = []
    data = []
    error_links = []
    init = time.time()
    for page in range(ptt_last_page, db_last_page, -1):
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


def update_ptt_unsold(links):
    data = []
    phone_dict = make_phone_dict()
    for i in range(8001, len(links)):
        d = links[i]
        url = d["link"]
        headers = {"Origin": "https://www.ptt.cc",
            "Referer": "https://fonts.googleapis.com/",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"}
            
        resp = requests.get(url, headers=headers)
        if "200" in str(resp):
            try:
                soup = BeautifulSoup(resp.text, "html.parser")

                # sold
                body = soup.find("body")
                if "已售" in body or "售出" in body or "已出售" in body:
                    sold = True
                else:
                    sold = False

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
                    price = d["price"]
                data.append((price, sold, url))
            except:
                print(url)
                data.append((d["price"], True, d["link"]))
        else:
            data.append((d["price"], True, d["link"]))

        if i%1000 == 0:
            db = Ptt()
            db.update_post(data)
            print("Insert {} Success.".format(i))
            data = []
        elif i%100 == 0:
            print(i)
    db = Ptt()
    db.update_post(data)
    print("Insert {} Success.".format(i))
    data = []    


if __name__ == '__main__':
    phone_dict = make_phone_dict()
    iphone_matches = make_iphone_matches(phone_dict)
    ptt_last_page = get_ptt_last_page("mobilesales")
    db_last_page = get_db_last_page("mobilesales")
    links = get_mobilesales_link(ptt_last_page, db_last_page)
    raw_data, data = crawl_mobilesales
    db = Ptt()
    db.insert_post(raw_data, data)
    
    ptt_last_page = get_ptt_last_page("MacShop")
    db_last_page = get_db_last_page("MacShop")
    max_page = Ptt().select_max_page_number("MacShop")
    main_macshop(db_last_page, ptt_last_page, phone_dict["iPhone"])

    links = Ptt().select_unsold_links()
    update_ptt_unsold(links)