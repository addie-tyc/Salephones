import requests
from bs4 import BeautifulSoup
from collections import defaultdict

ANDROID_URL = "https://en.wikipedia.org/wiki/List_of_Android_smartphones"
IPHONE_URL = "https://www.theiphonewiki.com/wiki/List_of_iPhones"

def make_phone_dict():
    url = ANDROID_URL
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    tables = soup.find_all("table", class_="wikitable")
    rows = []
    for i in tables:
        rows.extend(i.select("tbody tr th"))

    phones = [a.text.partition("(")[0].strip() for a in rows]
    phones = [ p for p in phones if len(p.split()) > 1]

    brands = set()
    for phone in phones:
        brands.add(phone.split(" ")[0])
    brands = list(brands)
    brands = sorted(brands)
    for brand in range(len(brands)):
        if brands[brand] == "Asus":
            brands = brands[brand:]
            break

    phone_dict = defaultdict(list)
    for brand in brands:
        if brand == "Samsung":
            for phone in phones:
                if phone.split(" ")[0] == brand:
                    if "/" in phone_dict:
                        p_lst = phone.split("/")
                        for series in p_lst[1:]:
                            sub_p = p_lst[0].replace(brand + " Galaxy", "").replace("5G", "").strip()
                            if series == "+":
                                phone = sub_p + series
                            else:
                                phone = sub_p + " " + series
                            if len(phone) > 0:
                                phone_dict[brand].append(phone)
                        phone_dict[brand].append(sub_p)
                    else:
                        phone = phone.replace(brand + " Galaxy", "").replace("5G", "").strip()
                        if len(phone) > 0:
                            phone_dict[brand].append(phone)
        elif brand == "POCO":
            for phone in phones:
                if phone.split(" ")[0] == brand:
                    phone = phone.replace("5G", "").strip()
                    if len(phone) > 0:
                        phone_dict["Xiaomi"].append(phone)

        elif brand == "Pixel":
            for phone in phones:
                if phone.split(" ")[0] == brand:
                    phone = phone.replace("5G", "").strip()
                    if len(phone) > 0:
                        phone_dict[brand].append(phone)
        else:
            for phone in phones:
                if phone.split(" ")[0] == brand:
                    if "/" in phone:
                        p_lst = phone.split("/")
                        for series in p_lst[1:]:
                            sub_p = p_lst[0].replace(brand, "").replace("5G", "").strip()
                            if series == "+":
                                phone = sub_p + series
                            else:
                                phone = sub_p + " " + series
                            if len(phone) > 0:
                                phone_dict[brand].append(phone)
                        phone_dict[brand].append(sub_p)
                    else:
                        phone = phone.replace(brand, "").replace("5G", "").strip()
                        if len(phone) > 0:
                            phone_dict[brand].append(phone)
                        phone_dict[brand].append(phone)
    phone_dict["Asus"].append("ROG Phone 2")
    phone_dict.pop("Galaxy")
    phone_dict.pop("Moto")

    url = IPHONE_URL
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


def get_phones():
    url = ANDROID_URL
    resp = requests.get(url, verify=False)
    soup = BeautifulSoup(resp.text, "html.parser")

    tables = soup.find_all("table", class_="wikitable")
    rows = []
    for i in tables:
        rows.extend(i.select("tbody tr th"))

    phones = [a.text.partition("(")[0].strip() for a in rows]
    phones = [ phone for phone in phones if len(phone.split()) > 1]

    brands = set()
    for phone in phones:
        brands.add(phone.split(" ")[0])
    brands = list(brands)
    brands = sorted(brands)
    for brand in range(len(brands)):
        if brands[brand] == "Asus":
            brands = brands[brand:]
            break

    phone_list = []
    for brand in brands:
        if brand == "Samsung":
            for phone in phones:
                if phone.split(" ")[0] == brand:
                    if "/" in phone:
                        p_lst = phone.split("/")
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
                        phone = phone.replace("5G", "").strip()
                        if len(phone) > 0:
                            phone_list.append(phone)
        elif brand == "POCO":
            for phone in phones:
                if phone.split(" ")[0] == brand:
                    phone = phone.replace("5G", "").strip()
                    if len(phone) > 0:
                        phone_list.append(phone)

        elif brand == "Pixel":
            for phone in phones:
                if phone.split(" ")[0] == brand:
                    phone = phone.replace("5G", "").strip()
                    if len(phone) > 0:
                        phone_list.append(phone)
        else:
            for phone in phones:
                if phone.split(" ")[0] == brand:
                    if "/" in phone:
                        p_lst = phone.split("/")
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
                        phone = phone.replace("5G", "").strip()
                        if len(phone) > 0:
                            phone_list.append(phone)
                        phone_list.append(phone)
    phone_list.append("Asus ROG Phone 2")

    url = IPHONE_URL
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
    for phone in phone_list:
        phone_set.add(phone)
    phone_list.append("Samsung Galaxy A71")
    phone_list = sorted(list(phone_set))
    remove_list = ["Asus ROG Phone II", "Release date", "Samsung Galaxy", "Samsung Galaxy A51 A71",
                   "Samsung Galaxy A51 A71 5G", "Samsung Galaxy A52 A52 5G"]
    for item in remove_list:
        phone_list.remove(item)
    return phone_list