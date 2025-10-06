pyinstaller main.py
	--clean --onefile --console
	--name=mascraper
	--contents-directory="data"
	--add-data="daterange.txt:."
	--add-data="data/band_blacklist.txt:data"
	--add-data="data/label_blacklist.txt:data"
	--add-data="data/theme_blacklist.txt:data"