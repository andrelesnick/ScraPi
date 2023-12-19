import time
from bs4 import BeautifulSoup as bs
import requests

from .Scraper import Scraper

class YoutubeScraper(Scraper):
    """
    Not a scraper really. Recover deleted videos from your liked videos
    Store video title, channel name, video id, date uploaded, date deleted in json list
    Have a folder "youtube" that contains all video thumbnails, title is id
    when a video is detected as deleted, send email with info + thumbnail

    maybe I can also detect unlisted videos?
    adapt this: https://github.com/fjolublar/youtube_playlist_tracker/blob/main/youtube_playlist.py
    https://developers.google.com/youtube/v3/docs/thumbnails
    how much space does it take to save a 480p/720p 30-second clip? If it's not too much, you could save a clip of the video as well
    maybe even run it through another compression algorithm to save space
    """
    def __init__(self):
        super().__init__()
        self.filename = 'youtube'
        self.name = 'Youtube Deleted Video Recovery'
        self.description = 'Recover deleted videos from your liked videos'
        self.frequency = 60*24
        # self.has_image = True
        # self.image_url = 'https://i.imgur.com/TVYVvGd.png'
        self.data = {
            'videos': [{
                'video_title': 'Placeholder - Remove this',
                'channel_title': 'Channel Name',
                'id': 'dQw4w9WgXcQ',
                'date_uploaded': '2021-01-01',
                'date_deleted': '2021-01-01',
                }]
            
        }
        self.get_storage()

    def scrape_data(self):
        url = 'https://cosmic-scans.com/manga/6969-tower-of-god/'
        response = requests.get(url)
        response.raise_for_status()
        soup = bs(response.text, 'lxml')
        new_chapter = int(soup.find('span', class_='epcur epcurlast').text.split(' ')[1])
        if new_chapter > self.data['latest_chapter']:
            self.last_update = time.time() # intended for urgent notifications; not implemented 
            self.data['latest_chapter'] = new_chapter
            push = {
                'type': 'push',
                'title': self.name,
                'body': f'Chapter {new_chapter} is now available at https://cosmicscans.com/tower-of-god-chapter-{new_chapter}/',
                'url': f'https://cosmic-scans.com/tower-of-god-chapter-{new_chapter}/',
            }
            return push
        return None
# create an instance
scraper = YoutubeScraper()
