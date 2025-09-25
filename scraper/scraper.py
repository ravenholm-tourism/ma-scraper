import httpx
import json
from json import JSONDecodeError
from bs4 import BeautifulSoup
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException


BASEURL = "https://www.metal-archives.com/"
PREFIX_RELURL = "browse/ajax-letter/l/"
POSTFIX_RELURL = "/json"
UPCOMING_URL = "release/ajax-upcoming/json/1"
URL = BASEURL + UPCOMING_URL

RELEASES_PER_PAGE = 100
HTTP2 = True
MA_TIMEOUT = 45.0

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-extensions")
driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(30)

def get_upcoming_resp(fromDate, toDate):
  params = {
    "fromDate": fromDate,
    "toDate": toDate
  }
  headers = {
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "User-Agent": "ToiletOvHell",
    "Accept-Encoding": "gzip, deflate"
  }
  with httpx.Client(http2=HTTP2, timeout=MA_TIMEOUT) as client:
    resp = client.get(URL, params=params, headers=headers)
  j = json.loads(resp.text)
  release_count = j["iTotalRecords"]
  releases = j["aaData"]

  # if > 100 releases, deal with pages
  release_max_index = release_count - 1
  page_count = release_max_index // RELEASES_PER_PAGE + 1 if release_max_index % RELEASES_PER_PAGE != 0 else release_max_index // RELEASES_PER_PAGE
  if page_count > 1:
    releases += get_additional_pages(params, headers, page_count)
  
  return releases, params, headers

def cleanup_releases(releases, headers):
  filtered_releases = []
  # only care about full-lengths, eps, and splits
  filtered_releases = [r for r in releases if r[2] in ("Full-length", "EP", "Split")]
  print(f"Number of LP, EP, and Split releases: {len(filtered_releases)}")

  # format releases so they can be copied directly to TovH
  formatted_releases = []
  for i, r in enumerate(filtered_releases):
    band = BeautifulSoup(r[0], features="lxml").find("a").text
    album = BeautifulSoup(r[1], features="lxml").find("a").text
    genre = r[3]

    album_url = BeautifulSoup(r[1], features="lxml").find("a")["href"]
    with httpx.Client(http2=HTTP2, timeout=MA_TIMEOUT) as client:
      album_resp = client.get(album_url, headers=headers)
    label_tag_parent = BeautifulSoup(album_resp.content, features="lxml").find_all("dl", class_="float_right")
    if len(label_tag_parent) == 1:
      label = label_tag_parent[0].select_one("dd").text
    else:
      label = "N/A"

    band_url = BeautifulSoup(r[0], features="lxml").find("a")["href"]
    with httpx.Client(http2=HTTP2, timeout=MA_TIMEOUT) as client:
      band_resp = client.get(band_url, headers=headers)
    themes_tag_parent = BeautifulSoup(band_resp.content, features="lxml").find_all("dl", class_="float_right")
    if len(themes_tag_parent) == 1:
      themes = themes_tag_parent[0].find_all("dd")[1].text
    else:
      themes = "N/A"
        
    ## filtering logic from blacklist
    with open("data/theme_blacklist.txt", "r") as f:
      ban_themes = [l.strip() for l in f]
      if themes in ban_themes:
          continue

    with open("data/label_blacklist.txt", "r") as f:
      ban_labels = [l.strip() for l in f]
      if label in ban_labels:
          continue

    with open("data/band_blacklist.txt", "r") as f:
      ban_bands = [l.strip() for l in f]
      if band in ban_bands:
          continue
    
    # print every 10th release
    if i % 10 == 0:
      print(f"Release #{i} finished.")

    bc_url = get_album_url(band, album)
    formatted_releases.append([band, album, label, genre, bc_url])

  return formatted_releases

def get_additional_pages(params, headers, page_count):
  releases = []
  for i in range(1, page_count):
    params["iDisplayStart"] = i * RELEASES_PER_PAGE
    with httpx.Client(http2=HTTP2, timeout=MA_TIMEOUT) as client:
      resp = client.get(URL, params=params, headers=headers)
    if resp.status_code == 200:
      j = json.loads(resp.text)
      releases += j["aaData"]
  return releases

def get_album_url(band, album):
  query = " ".join((band, album))
  search_url = "https://bandcamp.com/search?q=" + urllib.parse.quote_plus(query) + "&item_type=a"

  try:
    driver.get(search_url)
    results = driver.find_elements(By.CLASS_NAME, "searchresult")
    if len(results) > 0:
      el =  results[0]  # get first result
      album_name = el.find_element(By.CLASS_NAME, "heading").find_element(By.TAG_NAME, "a").text
      if album.lower().strip() in album_name.lower().strip():
        url = el.find_element(By.CLASS_NAME, "itemurl").find_element(By.TAG_NAME, "a").get_attribute("href")
        return url
      else:
        return None
  except TimeoutException as e:
    print(f"Album {album} by band {band} timed out searching bandcamp for an album link. Error: {e.msg}")
    return None

  return None
