#!/bin/env/python3

import sys
import scraper.formatter as sf

fromDate = ""
toDate = ""

try:
    with open("daterange.txt", "r") as f:
        fromDate = f.readline().strip()
        toDate = f.readline().strip()
        print(f"{fromDate=} {toDate=}")
except Exception as e:
    print("Error: ", str(e))
    sys.exit()

bc_links = sf.read_bc_output_file()
album_info = sf.read_tmp_album_info()
filename = "ttt_" + fromDate + "_" + toDate + "_html.txt"
release_list = []
for a in album_info:
  band = a["band"]
  album = a["album"]
  label = a["label"]
  genre = a["genre"]

  album_query = " ".join((a["band"], a["album"]))
  bc_match = [b for b in bc_links if b.get("query") == album_query][0]
  url = bc_match.get("link")

  if url is None:
    ln = '<b>' + band + ' - ' + album + ' (' + label + ') [' + genre + ']</b>\r\n'
  else:
    ln = '<b>' + band + ' - <a href="' + url + '" target="_blank" rel="noopener">' + album + '</a> (' + label + ') [' + genre + ']</b>\r\n'
  ln += "\r\n"

  release_list.append(ln)

release_list.sort()
with open(filename, "w", encoding="utf-8") as f:
  f.writelines(release_list)

print("done")
