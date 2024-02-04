import scraper.scraper as s
import sys

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

releases = s.get_upcoming_resp(fromDate, toDate)
filename = "ttt_" + fromDate + "_" + toDate + "_html.txt"
release_list = []
for r in releases:
    band = r[0]
    album = r[1]
    label = r[3]
    genre = r[4]
    url = r[5]
    if url is None:
        ln = '<b>' + band + ' - ' + album + ' (' + label + ') [' + genre + ']</b>\r\n'
    else:
        ln = '<b>' + band + ' - </b><a href="' + url + '">' + album + '</a><b> (' + label + ') [' + genre + ']</b>\r\n'
    release_list.append(ln)
        
release_list.sort()
with open(filename, "w") as f:
    f.writelines(release_list)
    
print("done")
