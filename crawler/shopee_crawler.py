import requests
import urllib
from datetime import datetime
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import time
import random
import re
from collections import defaultdict
import os

from crawler_model import Ptt
from util import make_phone_dict, make_iphone_matches


PRICE_FLOOR = 999
PRICE_SCALAR = 100000 # modifying shopee price
def gen_header_search(keyword):
    ua = UserAgent()
    fakeua = ua.random
    headers = {
    'User-Agent': fakeua,
    'x-api-source': 'pc',
    'referer': f'https://shopee.tw/search?keyword={urllib.parse.quote(keyword)}'
    }
    return headers


def gen_header(referer):
    ua = UserAgent()
    fakeua = ua.random
    headers = {
    'User-Agent': fakeua,
    'x-api-source': 'pc',
    'referer': referer
    }
    return headers


proxy_lst = ['http://tihyjcyk-dest:sr9mbjac4xab@193.8.231.209:9215',
 'http://tihyjcyk-dest:sr9mbjac4xab@107.152.177.67:6087',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.57.168.196:7200',
 'http://tihyjcyk-dest:sr9mbjac4xab@138.122.194.254:7330',
 'http://tihyjcyk-dest:sr9mbjac4xab@104.144.26.137:8667',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.154.244.123:8161',
 'http://tihyjcyk-dest:sr9mbjac4xab@185.102.50.157:7240',
 'http://tihyjcyk-dest:sr9mbjac4xab@5.154.253.240:8498',
 'http://tihyjcyk-dest:sr9mbjac4xab@185.242.94.107:6192',
 'http://tihyjcyk-dest:sr9mbjac4xab@5.154.253.113:8371',
 'http://tihyjcyk-dest:sr9mbjac4xab@185.242.95.181:6522',
 'http://tihyjcyk-dest:sr9mbjac4xab@5.157.130.161:8165',
 'http://tihyjcyk-dest:sr9mbjac4xab@194.33.61.45:8628',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.130.60.93:9620',
 'http://tihyjcyk-dest:sr9mbjac4xab@194.33.61.44:8627',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.154.84.190:8241',
 'http://tihyjcyk-dest:sr9mbjac4xab@91.246.195.28:6797',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.137.80.64:9084',
 'http://tihyjcyk-dest:sr9mbjac4xab@37.35.40.21:8111',
 'http://tihyjcyk-dest:sr9mbjac4xab@64.43.90.245:6760',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.140.14.98:8114',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.136.231.236:7292',
 'http://tihyjcyk-dest:sr9mbjac4xab@182.54.239.228:8245',
 'http://tihyjcyk-dest:sr9mbjac4xab@176.116.231.240:7582',
 'http://tihyjcyk-dest:sr9mbjac4xab@64.43.90.91:6606',
 'http://tihyjcyk-dest:sr9mbjac4xab@193.151.160.34:8121',
 'http://tihyjcyk-dest:sr9mbjac4xab@193.27.10.54:6139',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.136.231.128:7184',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.72.55.91:7128',
 'http://tihyjcyk-dest:sr9mbjac4xab@185.102.48.143:6225',
 'http://tihyjcyk-dest:sr9mbjac4xab@182.54.239.8:8025',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.94.47.183:8227',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.140.13.98:9111',
 'http://tihyjcyk-dest:sr9mbjac4xab@185.102.48.186:6268',
 'http://tihyjcyk-dest:sr9mbjac4xab@194.31.162.173:7689',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.131.212.36:6085',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.87.249.71:7649',
 'http://tihyjcyk-dest:sr9mbjac4xab@5.154.253.123:8381',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.72.55.118:7155',
 'http://tihyjcyk-dest:sr9mbjac4xab@185.242.94.47:6132',
 'http://tihyjcyk-dest:sr9mbjac4xab@185.242.93.101:8441',
 'http://tihyjcyk-dest:sr9mbjac4xab@37.35.41.215:8561',
 'http://tihyjcyk-dest:sr9mbjac4xab@37.35.43.48:8906',
 'http://tihyjcyk-dest:sr9mbjac4xab@5.154.254.244:5255',
 'http://tihyjcyk-dest:sr9mbjac4xab@193.151.160.198:8285',
 'http://tihyjcyk-dest:sr9mbjac4xab@5.157.130.1:8005',
 'http://tihyjcyk-dest:sr9mbjac4xab@192.156.217.96:7170',
 'http://tihyjcyk-dest:sr9mbjac4xab@193.23.253.161:7733',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.137.40.128:8681',
 'http://tihyjcyk-dest:sr9mbjac4xab@192.156.217.58:7132',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.131.212.215:6264',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.72.55.37:7074',
 'http://tihyjcyk-dest:sr9mbjac4xab@193.8.215.188:8207',
 'http://tihyjcyk-dest:sr9mbjac4xab@192.153.171.192:6265',
 'http://tihyjcyk-dest:sr9mbjac4xab@193.23.253.152:7724',
 'http://tihyjcyk-dest:sr9mbjac4xab@5.157.130.70:8074',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.92.247.229:6737',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.72.55.80:7117',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.130.60.202:9729',
 'http://tihyjcyk-dest:sr9mbjac4xab@192.153.171.10:6083',
 'http://tihyjcyk-dest:sr9mbjac4xab@193.23.253.52:7624',
 'http://tihyjcyk-dest:sr9mbjac4xab@176.116.231.126:7468',
 'http://tihyjcyk-dest:sr9mbjac4xab@193.23.253.236:7808',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.131.212.76:6125',
 'http://tihyjcyk-dest:sr9mbjac4xab@193.8.215.211:8230',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.137.40.12:8565',
 'http://tihyjcyk-dest:sr9mbjac4xab@193.151.161.60:8403',
 'http://tihyjcyk-dest:sr9mbjac4xab@193.151.161.111:8454',
 'http://tihyjcyk-dest:sr9mbjac4xab@193.151.161.116:8459',
 'http://tihyjcyk-dest:sr9mbjac4xab@5.157.130.189:8193',
 'http://tihyjcyk-dest:sr9mbjac4xab@176.116.231.117:7459',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.131.213.90:7638',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.87.249.101:7679',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.87.249.140:7718',
 'http://tihyjcyk-dest:sr9mbjac4xab@5.154.253.215:8473',
 'http://tihyjcyk-dest:sr9mbjac4xab@192.198.126.10:7053',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.130.60.42:9569',
 'http://tihyjcyk-dest:sr9mbjac4xab@5.157.131.212:8472',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.130.60.105:9632',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.131.212.251:6300',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.131.212.194:6243',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.130.60.76:9603',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.92.247.31:6539',
 'http://tihyjcyk-dest:sr9mbjac4xab@176.116.230.220:7306',
 'http://tihyjcyk-dest:sr9mbjac4xab@193.8.231.204:9210',
 'http://tihyjcyk-dest:sr9mbjac4xab@5.154.253.209:8467',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.92.247.187:6695',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.87.249.235:7813',
 'http://tihyjcyk-dest:sr9mbjac4xab@193.8.231.129:9135',
 'http://tihyjcyk-dest:sr9mbjac4xab@2.56.101.231:8763',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.92.247.176:6684',
 'http://tihyjcyk-dest:sr9mbjac4xab@2.56.101.12:8544',
 'http://tihyjcyk-dest:sr9mbjac4xab@2.56.101.69:8601',
 'http://tihyjcyk-dest:sr9mbjac4xab@195.158.192.228:8805',
 'http://tihyjcyk-dest:sr9mbjac4xab@195.158.192.241:8818',
 'http://tihyjcyk-dest:sr9mbjac4xab@45.92.247.189:6697',
 'http://tihyjcyk-dest:sr9mbjac4xab@85.209.129.154:8694',
 'http://tihyjcyk-dest:sr9mbjac4xab@2.56.101.122:8654',
 'http://tihyjcyk-dest:sr9mbjac4xab@85.209.130.132:7673',
 'http://tihyjcyk-dest:sr9mbjac4xab@193.8.231.21:9027']


phone_dict = make_phone_dict()
iphone_matches = make_iphone_matches()
def get_title_storage(phone_dict=phone_dict, iphone_matches=iphone_matches, title=""):
    if ("紅米" in title.lower()) or ("redmi" in title.lower()):
        title = "Redmi" + " " + title
    elif ("小米" in title.lower()) or ("poco" in title.lower()):
        title = "Xiaomi" + " " + title
    elif ("三星" in title.lower()) and ("samsung" in title.lower()):
        title = "Samsung" + " " + title
    elif ( "zenfone" in title.lower() or "rog" in title.lower() ) and ("asus" not in title.lower()):
        title = "Asus" + " " + title

    title = " ".join(re.findall(r"[a-zA-Z0-9+]+", title))
    storage = None

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
    random.shuffle(proxy_lst)
    proxy_chosen = proxy_lst[:int(end / step)]
    i = 0
    headers = gen_header_search(keyword)
    s = requests.Session()
    s.keep_alive = False
    s.trust_env = False
    url = 'https://shopee.tw/api/v4/search/product_labels'
    p = proxy_chosen[int(i/step)]
    proxies = {"http": p, "https": p}
    try:
        r = s.get(url, headers=headers, proxies=proxies)
    except requests.exceptions.ProxyError:
        proxy_chosen.pop(int(i/step))
        proxy_chosen.append(proxy_chosen[int(i/step)-1])
        p = proxy_chosen[int(i/step)]
        proxies = {"http": p, "https": p}
        r = s.get(url, headers=headers, proxies=proxies)

    while i < end:
        p = proxy_chosen[int(i/step)]
        proxies = {"http": p, "https": p}
        base_url = 'https://shopee.tw/api/v2/search_items/'
        query = f"by=relevancy&conditions=used&keyword={keyword}&limit={step}&newest={i}&order=desc&page_type=search&min_price=2000&scenario=PAGE_GLOBAL_SEARCH&skip_autocorrect=1&version=2"

        url = base_url + '?' + query
        r = s.get(url, headers=headers, proxies=proxies)
        if r.status_code == requests.codes.ok:
            res_json = r.json()
            items = sorted(res_json["items"], key=lambda d: d["ctime"])
            if items[-1]["ctime"] > datetime.timestamp(datetime.now()):
                proxy_chosen.pop(int(i / step))
                proxy_chosen.append(proxy_chosen[int(i / step)-1])
                print("Take a rest!")
                time.sleep(30)
            else:   
                for d in items:
                    if int(d["price"] / PRICE_SCALAR) > PRICE_FLOOR:
                        start = time.time()
                        rf = f'https://shopee.tw/product/{d["shopid"]}/{d["itemid"]}'
                        headers = gen_header(rf)
                        url = f'https://shopee.tw/api/v2/item/get?itemid={d["itemid"]}&shopid={d["shopid"]}'
                        r = requests.get(url, headers=headers)
                        item = r.json()["item"]
                        title, storage = get_title_storage(title=d["name"])
                        data.append(
                                (
                                title,
                                storage,
                                (int(d["price"] / PRICE_SCALAR)), # price
                                False, # new
                                (item["status"] == "sold_out"), # sold
                                item["description"].replace("\n", "。"), # box
                                f'https://shopee.tw/product/{d["shopid"]}/{d["itemid"]}', # link
                                datetime.utcfromtimestamp(d["ctime"]).strftime('%Y-%m-%d %H:%M:%S'), # created_at
                                "shopee" # source
                                ) 
                            )
                if i%500 == 0:
                    db = Ptt()
                    db.insert_shopee(data)
                    print("Insert {} Done".format(i))
                    data = []
                i += step
                print(i, len(data))
        else:
            i += step


if __name__ == "__main__":
    crawl_shopee()