#!/bin/env/python3

import sys
import scraper.scraper as s

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

releases, params, headers = s.get_upcoming_resp(fromDate, toDate)
s.generate_extension_input(releases, headers)
# filename = "ttt_" + fromDate + "_" + toDate + "_html.txt"
# release_list = []
# for r in formatted_releases:
#     band = r[0]
#     album = r[1]
#     label = r[2]
#     genre = r[3]
#     url = r[4]
#     if url is None:
#         ln = '<b>' + band + ' - ' + album + ' (' + label + ') [' + genre + ']</b>\r\n'
#     else:
#         ln = '<b>' + band + ' - <a href="' + url + '" target="_blank" rel="noopener">' + album + '</a> (' + label + ') [' + genre + ']</b>\r\n'
#     if sys.platform == "linux":
#         ln += "\r\n"
#     release_list.append(ln)
        
# release_list.sort()
# with open(filename, "w", encoding="utf-8") as f:
#     f.writelines(release_list)

# print("done")
