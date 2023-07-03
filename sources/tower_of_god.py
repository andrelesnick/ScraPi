import time
from bs4 import BeautifulSoup as bs
import requests

from .Scraper import Scraper

class TowerOfGodScraper(Scraper):
    def __init__(self): # filename defaults to empty string if not provided
        super().__init__()
        self.filename = 'tower_of_god'
        self.name = 'Tower of God'
        self.description = 'Receive updates Cosmic Scans releases for Tower of God.'
        self.frequency = 5
        # self.urgent_frequency = 5
        # self.urgent_days = 6
        self.has_image = True
        self.image_url = 'https://i.imgur.com/TVYVvGd.png'
        self.data = {
            'latest_chapter': 500
        }
        self.get_storage()

    def scrape_data(self):
        url = 'https://cosmicscans.com/manga/6969-tower-of-god/'
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
                'url': f'https://cosmicscans.com/tower-of-god-chapter-{new_chapter}/',
            }
            return push
        return None
# create an instance
scraper = TowerOfGodScraper()
