import time
import requests
import json
from json import JSONDecodeError
import re
from ratelimit import limits, sleep_and_retry
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options




BASEURL = "https://www.metal-archives.com/"
PREFIX_RELURL = "browse/ajax-letter/l/"
POSTFIX_RELURL = "/json"
UPCOMING_URL = "release/ajax-upcoming/json/1"

starttime = time.time()
runcount = 0

options = Options()
options.add_argument("--headless=new")
d = webdriver.Chrome(options=options)

@sleep_and_retry
def get_upcoming_resp(fromDate, toDate):
    params = {
        "iColumns": 6,
        "includeVersions": 0,
        "fromDate": fromDate,
        "toDate": toDate
    }
    headers = {
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "User-Agent": "ToiletOvHell",
        "Accept-Encoding": "gzip, deflate"
    }
    resp = requests.request("GET", BASEURL + UPCOMING_URL, params=params, headers=headers)
    _s = resp.text
    print(_s)
    # ix = _s.find('"sEcho":') + 8
    # s = _s[:ix] + "0" + _s[ix:]
    j = json.loads(_s)
    print("Total Entries", j["iTotalRecords"])
    # TODO if > 100, deal with pages
    all_releases = j["aaData"]
    releases = [r for r in all_releases if r[2] in ("Full-length", "EP", "Split")]
    
    clean_releases = []
    for i, r in enumerate(releases):
        if i % 10 == 0:
            print(f"getting release {i}")
        band = BeautifulSoup(r[0], features="lxml").find("a").text
        album = BeautifulSoup(r[1], features="lxml").find("a").text
        album_url = BeautifulSoup(r[1], features="lxml").find("a")["href"]
        album_resp = requests.request("GET", album_url, headers=headers)
        label_tag_parent = BeautifulSoup(album_resp.content, features="lxml").find_all("dl", class_="float_right")
        if len(label_tag_parent) == 1:
            label = label_tag_parent[0].select_one("dd").text
        else:
            label = "N/A"
        
        band_url = BeautifulSoup(r[0], features="lxml").find("a")["href"]
        band_resp = requests.request("GET", band_url, headers=headers)
        themes_tag_parent = BeautifulSoup(band_resp.content, features="lxml").find_all("dl", class_="float_right")
        if len(themes_tag_parent) == 1:
            themes = themes_tag_parent[0].find_all("dd")[1].text
        else:
            themes = "N/A"
        
        ## themes filtering logic
        with open("data/theme_blacklist.txt", "r") as f:
            ban_themes = [l.strip() for l in f]
            if themes in ban_themes:
                continue

        ## label filtering logic
        with open("data/label_blacklist.txt", "r") as f:
            ban_labels = [l.strip() for l in f]
            if label in ban_labels:
                continue

        ## band filtering logic
        with open("data/band_blacklist.txt", "r") as f:
            ban_bands = [l.strip() for l in f]
            if band in ban_bands:
                continue
        
        bc_url = get_album_url(band, album)
        clean_releases.append([band, album, r[2], label, r[3], bc_url])

    return clean_releases
    
    
    




@sleep_and_retry
# @limits(15, period=900)
def get_alpha_resp(letter="A", start=0, length=500):
    ## gets all bands starting with letter
    payload = {
        "sEcho": 0,
        "iDisplayStart": start,
        "iDisplayLength": length
    }
    resp = requests.get(BASEURL + PREFIX_RELURL + letter + POSTFIX_RELURL, params=payload)
    print(resp.status_code)
    # print(resp.headers)
    # print(resp.text[:70])
    # print(resp.text.find("sEcho"))
    # print(resp.text.find(": ,"))
    _noval = resp.text.find(": ,")
    print(_noval) 
    txt = resp.text[:_noval+2] + "0" + resp.text[_noval+2:]     #HACK: response is an invalid json with a key that's missing a value, so I add one
    global runcount
    runcount +=1
    if resp.text != '0':
        j = json.loads(txt)
    else:
        elapsed = time.time()-starttime
        print("seconds elapsed:", elapsed)
        print("successfull calls:", runcount)
        raise Exception("rate limited by cloudflare")
    return j

def get_bandlist(j):
    bandlist = {
        'url': [],
        'name': [],
        'country': [],
        'genre': [],
        'status': []
    }

    # loop through bands in json and add to bandlist dict
    for r in j['aaData']:
        url = re.findall("href=[\"\'](.*?)[\"\']", r[0])
        bandlist['url'].append(url[0])
        name = re.findall(">(.*?)<", r[0])
        bandlist['name'].append(name[0])
        status = re.findall(">(.*?)<", r[3])
        bandlist['status'].append(status[0])
        bandlist['country'].append(r[1])
        bandlist['genre'].append(r[2])

    return bandlist

def get_album_url(band, album):
    query = " ".join((band, album))
    search_url = "https://bandcamp.com/search?q=" + urllib.parse.quote_plus(query) + "&item_type=a"

    d.get(search_url)
    results = d.find_elements(By.CLASS_NAME, "searchresult")
    if len(results) > 0:
        el =  results[0]    # get first result
        album_name = el.find_element(By.CLASS_NAME, "heading").find_element(By.TAG_NAME, "a").text
        if album_name.lower().strip() == album.lower().strip():
            url = el.find_element(By.CLASS_NAME, "itemurl").find_element(By.TAG_NAME, "a").text
            return url
        else:
            return None
    return None
    
