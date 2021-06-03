import requests
import urllib
from datetime import datetime
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import time
import random
import re
from collections import defaultdict

from crawler_model import Ptt

def gen_header_search(keyword):
    ua = UserAgent()
    fakeua = ua.random
    headers = {
    'user-agent': fakeua,
    'x-api-source': 'pc',
    'referer': f'https://shopee.tw/search?keyword={urllib.parse.quote(keyword)}'
    }
    return headers

def gen_header(keyword, referer):
    ua = UserAgent()
    fakeua = ua.random
    headers = {
    'user-agent': fakeua,
    'x-api-source': 'pc',
    'referer': referer
    }
    return headers

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

        elif b == "Pixel":
            for p in phones:
                if p.split(" ")[0] == b:
                    phone = p.replace("5G", "").strip()
                    if len(phone) > 0:
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

    for k in phone_dict.keys():
        phone_dict[k] = sorted(phone_dict[k], key=lambda x: len(x), reverse=True)

    return phone_dict

proxy_lst = ['http://tihyjcyk-dest:sr9mbjac4xab@45.15.223.0:9018', 'http://tihyjcyk-dest:sr9mbjac4xab@45.146.180.69:9139', 'http://tihyjcyk-dest:sr9mbjac4xab@107.152.222.227:9250', 'http://tihyjcyk-dest:sr9mbjac4xab@45.128.247.174:7675', 'http://tihyjcyk-dest:sr9mbjac4xab@107.152.197.223:8245', 'http://tihyjcyk-dest:sr9mbjac4xab@45.94.47.121:8165', 'http://tihyjcyk-dest:sr9mbjac4xab@181.177.91.167:8740', 'http://tihyjcyk-dest:sr9mbjac4xab@144.168.241.216:8810', 'http://tihyjcyk-dest:sr9mbjac4xab@85.209.130.100:7641', 'http://tihyjcyk-dest:sr9mbjac4xab@45.142.28.114:8125', 'http://tihyjcyk-dest:sr9mbjac4xab@45.137.84.15:7065', 'http://tihyjcyk-dest:sr9mbjac4xab@91.246.193.60:6317', 'http://tihyjcyk-dest:sr9mbjac4xab@45.154.56.114:7132', 'http://tihyjcyk-dest:sr9mbjac4xab@91.246.194.18:6531', 'http://tihyjcyk-dest:sr9mbjac4xab@193.23.253.69:7641', 'http://tihyjcyk-dest:sr9mbjac4xab@193.27.10.145:6230', 'http://tihyjcyk-dest:sr9mbjac4xab@5.154.253.30:8288', 'http://tihyjcyk-dest:sr9mbjac4xab@185.95.157.83:6104', 'http://tihyjcyk-dest:sr9mbjac4xab@45.128.245.61:9072', 'http://tihyjcyk-dest:sr9mbjac4xab@193.5.251.127:7634', 'http://tihyjcyk-dest:sr9mbjac4xab@45.154.58.50:7563', 'http://tihyjcyk-dest:sr9mbjac4xab@109.207.130.19:8026', 'http://tihyjcyk-dest:sr9mbjac4xab@45.9.122.183:8264', 'http://tihyjcyk-dest:sr9mbjac4xab@2.56.101.189:8721', 'http://tihyjcyk-dest:sr9mbjac4xab@45.154.58.133:7646', 'http://tihyjcyk-dest:sr9mbjac4xab@185.245.27.157:6930', 'http://tihyjcyk-dest:sr9mbjac4xab@5.157.130.247:8251', 'http://tihyjcyk-dest:sr9mbjac4xab@185.245.27.137:6910', 'http://tihyjcyk-dest:sr9mbjac4xab@37.35.40.139:8229', 'http://tihyjcyk-dest:sr9mbjac4xab@176.116.231.146:7488', 'http://tihyjcyk-dest:sr9mbjac4xab@91.246.192.118:6119', 'http://tihyjcyk-dest:sr9mbjac4xab@193.27.23.101:9189', 'http://tihyjcyk-dest:sr9mbjac4xab@200.0.61.246:6321', 'http://tihyjcyk-dest:sr9mbjac4xab@176.116.230.111:7197', 'http://tihyjcyk-dest:sr9mbjac4xab@185.245.26.2:6519', 'http://tihyjcyk-dest:sr9mbjac4xab@200.0.61.74:6149', 'http://tihyjcyk-dest:sr9mbjac4xab@37.35.41.124:8470', 'http://tihyjcyk-dest:sr9mbjac4xab@185.205.194.228:7748', 'http://tihyjcyk-dest:sr9mbjac4xab@193.8.231.198:9204', 'http://tihyjcyk-dest:sr9mbjac4xab@45.154.244.47:8085', 'http://tihyjcyk-dest:sr9mbjac4xab@84.21.188.31:8565', 'http://tihyjcyk-dest:sr9mbjac4xab@64.43.91.183:6954', 'http://tihyjcyk-dest:sr9mbjac4xab@64.43.90.82:6597', 'http://tihyjcyk-dest:sr9mbjac4xab@185.95.157.166:6187', 'http://tihyjcyk-dest:sr9mbjac4xab@45.137.43.35:7589', 'http://tihyjcyk-dest:sr9mbjac4xab@185.205.194.175:7695', 'http://tihyjcyk-dest:sr9mbjac4xab@45.154.84.72:8123', 'http://tihyjcyk-dest:sr9mbjac4xab@85.209.129.127:8667', 'http://tihyjcyk-dest:sr9mbjac4xab@200.0.61.213:6288', 'http://tihyjcyk-dest:sr9mbjac4xab@45.155.70.242:8252', 'http://tihyjcyk-dest:sr9mbjac4xab@45.137.40.176:8729', 'http://tihyjcyk-dest:sr9mbjac4xab@37.35.40.188:8278', 'http://tihyjcyk-dest:sr9mbjac4xab@176.116.230.61:7147', 'http://tihyjcyk-dest:sr9mbjac4xab@45.87.249.192:7770', 'http://tihyjcyk-dest:sr9mbjac4xab@37.35.40.185:8275', 'http://tihyjcyk-dest:sr9mbjac4xab@5.154.253.219:8477', 'http://tihyjcyk-dest:sr9mbjac4xab@5.157.130.77:8081', 'http://tihyjcyk-dest:sr9mbjac4xab@45.131.212.146:6195', 'http://tihyjcyk-dest:sr9mbjac4xab@5.154.253.155:8413', 'http://tihyjcyk-dest:sr9mbjac4xab@176.116.231.110:7452', 'http://tihyjcyk-dest:sr9mbjac4xab@193.23.253.82:7654', 'http://tihyjcyk-dest:sr9mbjac4xab@45.92.247.84:6592', 'http://tihyjcyk-dest:sr9mbjac4xab@45.130.60.81:9608', 'http://tihyjcyk-dest:sr9mbjac4xab@85.209.129.114:8654', 'http://tihyjcyk-dest:sr9mbjac4xab@45.131.212.68:6117', 'http://tihyjcyk-dest:sr9mbjac4xab@45.72.55.105:7142', 'http://tihyjcyk-dest:sr9mbjac4xab@2.56.101.175:8707', 'http://tihyjcyk-dest:sr9mbjac4xab@85.209.130.145:7686', 'http://tihyjcyk-dest:sr9mbjac4xab@45.86.15.18:8565', 'http://tihyjcyk-dest:sr9mbjac4xab@5.154.253.114:8372', 'http://tihyjcyk-dest:sr9mbjac4xab@193.23.253.88:7660', 'http://tihyjcyk-dest:sr9mbjac4xab@193.23.253.115:7687', 'http://tihyjcyk-dest:sr9mbjac4xab@45.72.55.201:7238', 'http://tihyjcyk-dest:sr9mbjac4xab@45.72.55.127:7164', 'http://tihyjcyk-dest:sr9mbjac4xab@45.72.55.200:7237', 'http://tihyjcyk-dest:sr9mbjac4xab@45.72.55.174:7211', 'http://tihyjcyk-dest:sr9mbjac4xab@45.130.60.129:9656', 'http://tihyjcyk-dest:sr9mbjac4xab@45.130.60.228:9755', 'http://tihyjcyk-dest:sr9mbjac4xab@45.130.60.123:9650', 'http://tihyjcyk-dest:sr9mbjac4xab@2.56.101.136:8668', 'http://tihyjcyk-dest:sr9mbjac4xab@45.92.247.166:6674', 'http://tihyjcyk-dest:sr9mbjac4xab@45.131.212.244:6293', 'http://tihyjcyk-dest:sr9mbjac4xab@185.95.157.190:6211', 'http://tihyjcyk-dest:sr9mbjac4xab@45.87.249.197:7775', 'http://tihyjcyk-dest:sr9mbjac4xab@185.95.157.131:6152', 'http://tihyjcyk-dest:sr9mbjac4xab@45.131.212.246:6295', 'http://tihyjcyk-dest:sr9mbjac4xab@45.87.249.15:7593', 'http://tihyjcyk-dest:sr9mbjac4xab@45.92.247.197:6705', 'http://tihyjcyk-dest:sr9mbjac4xab@2.56.101.219:8751', 'http://tihyjcyk-dest:sr9mbjac4xab@45.130.60.107:9634', 'http://tihyjcyk-dest:sr9mbjac4xab@185.95.157.117:6138', 'http://tihyjcyk-dest:sr9mbjac4xab@45.131.212.138:6187', 'http://tihyjcyk-dest:sr9mbjac4xab@45.92.247.141:6649', 'http://tihyjcyk-dest:sr9mbjac4xab@45.92.247.241:6749', 'http://tihyjcyk-dest:sr9mbjac4xab@45.87.249.249:7827', 'http://tihyjcyk-dest:sr9mbjac4xab@193.151.160.57:8144', 'http://tihyjcyk-dest:sr9mbjac4xab@193.151.160.143:8230', 'http://tihyjcyk-dest:sr9mbjac4xab@193.151.161.119:8462', 'http://tihyjcyk-dest:sr9mbjac4xab@193.151.161.60:8403']

phone_dict = make_phone_dict()
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

def get_title_storage(phone_dict=phone_dict, iphone_matches=iphone_matches, title=""):
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
    return title, storage

def crawl_shopee(proxy_lst=proxy_lst, end=5000, step=50):
    data = []
    keyword = "二手手機"
    init = time.time()
    random.shuffle(proxy_lst)
    proxy_chosen = proxy_lst[:int(end/step)]
    i = 2550
    while i < end:
        p = proxy_chosen[int(i/step)%100]
        proxies = {"http": p, "https": p}
        headers = gen_header_search(keyword)
        s = requests.Session()
        url = 'https://shopee.tw/api/v4/search/product_labels'
        r = s.get(url, headers=headers, proxies=proxies)

        base_url = 'https://shopee.tw/api/v2/search_items/'
        query = f"by=relevancy&conditions=used&keyword={keyword}&limit={step}&newest={i}&order=desc&page_type=search&min_price=2000&scenario=PAGE_GLOBAL_SEARCH&skip_autocorrect=1&version=2"

        url = base_url + '?' + query
        r = s.get(url, headers=headers, proxies=proxies)
        print(time.time()-init)
        if r.status_code == requests.codes.ok:
            res_json = r.json()
            items = sorted(res_json["items"], key=lambda d: d["ctime"])
            if items[-1]["ctime"] > datetime.timestamp(datetime.now()):
                time.sleep(30)
                proxy_chosen.pop(int(i/step)%100)
                proxy_chosen.append(random.choice(proxy_lst))
                print("Take a rest!")
            else:   
                for d in items:
                    if int(d["price"]/100000) > 2000:
                        start = time.time()
                        rf = f'https://shopee.tw/product/{d["shopid"]}/{d["itemid"]}'
                        headers = gen_header(keyword, rf)
                        url = f'https://shopee.tw/api/v2/item/get?itemid={d["itemid"]}&shopid={d["shopid"]}'
                        r = requests.get(url, headers=headers)
                        item = r.json()["item"]
                        title, storage = get_title_storage(title=d["name"])
                        data.append(
                                (
                                title,
                                storage,
                                (int(d["price"]/100000)), # price
                                False, # new
                                (item["status"] == "sold_out"), # sold
                                item["description"].replace("\n", "。"), # box
                                f'https://shopee.tw/product/{d["shopid"]}/{d["itemid"]}', # link
                                datetime.utcfromtimestamp(d["ctime"]).strftime('%Y-%m-%d %H:%M:%S'), # created_at
                                "shopee" # source
                                ) 
                            )
                        print(time.time()-start)
                if i%500 == 0:
                    db = Ptt()
                    db.insert_shopee(data)
                    print("Insert {} Done".format(i))
                    data = []
                i += step
                print(i, len(data))
        else:
            i += step
    print(time.time()-init)

if __name__ == "__main__":
    crawl_shopee()