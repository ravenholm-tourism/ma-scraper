import httpx
import json
from bs4 import BeautifulSoup

BASEURL = "https://www.metal-archives.com/"
PREFIX_RELURL = "browse/ajax-letter/l/"
POSTFIX_RELURL = "/json"
UPCOMING_URL = "release/ajax-upcoming/json/1"
URL = BASEURL + UPCOMING_URL

RELEASES_PER_PAGE = 100
HTTP2 = True
MA_TIMEOUT = 45.0

BC_ALBUM_LIST = []
BC_ALBUM_LIST_INPUT_FILE = "copy_me_to_bc_extension.txt"
ALBUM_INFO_TMP = "tmp/album_info.json"

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

def generate_extension_input(releases, headers):
  filtered_releases = []
  # only care about full-lengths, eps, and splits
  filtered_releases = [r for r in releases if r[2] in ("Full-length", "EP", "Split")]
  print(f"Number of LP, EP, and Split releases: {len(filtered_releases)}")

  # format releases so they can be copied directly to TovH
  formatted_releases = []
  for i, r in enumerate(filtered_releases):
    formatted_release = dict.fromkeys(["band", "album", "label", "genre", "bc_url"])
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

    formatted_release.update({
      "band": band,
      "album": album,
      "label": label,
      "genre": genre
    })

    formatted_releases.append(formatted_release)
    
    append_to_bc_album_list(band, album)
  
  with open(ALBUM_INFO_TMP, "w") as f:
    json.dump(formatted_releases, f)
  
  write_bc_album_list_to_file()
  
  print("List of artists + albums to copy to browser extension saved to", BC_ALBUM_LIST_INPUT_FILE)

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

def append_to_bc_album_list(band, album):
  line = " ".join((band, album)) + "\r\n"
  BC_ALBUM_LIST.append(line)

def write_bc_album_list_to_file():
  with open(BC_ALBUM_LIST_INPUT_FILE, "w") as f:
    f.writelines(BC_ALBUM_LIST)

