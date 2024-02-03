import scraper.scraper as s

class TestGetAlbumUrl:
    
    def test_top_result(self):
        band = "cult leader"
        album = "a patient man"
        url = s.get_album_url(band, album)
        # print(url)
        assert url == "https://cultleadermusic.bandcamp.com/album/a-patient-man"
    
    def test_no_matches(self):
        band = "orchid"
        album = "chaos is me"
        url = s.get_album_url(band, album)
        # print(url)
        assert url is None
    
    def test_no_search_results(self):
        band = "asdfqwer"
        album = "vbnbm"
        url = s.get_album_url(band, album)
        # print(url)
        assert url is None
