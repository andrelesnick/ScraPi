import time
from bs4 import BeautifulSoup as bs
import requests

import sys
sys.path.append("..") # Adds higher directory to python modules path.
from .Scraper import Scraper

class TowerOfGodScraper(Scraper):
    def __init__(self): # filename defaults to empty string if not provided
        super().__init__()
        self.filename = 'tower_of_god'
        self.frequency = 5
        # self.urgent_frequency = 5
        # self.urgent_days = 6
        self.data = {
            'latest_chapter': '500',
        }
        self.get_storage()

    def scrape_data(self):
        url = 'https://cosmicscans.com/manga/12423-tower-of-god/'
        response = requests.get(url)
        response.raise_for_status()
        soup = bs(response.text, 'lxml')
        new_chapter = int(soup.find('span', class_='epcur epcurlast').text.split(' ')[1])
        if new_chapter > int(self.data['latest_chapter']):
            self.last_update = time.time()
            self.data['latest_chapter'] = str(new_chapter)
            push = {
                'type': 'push',
                'title': 'Tower of God',
                'body': f'Chapter {new_chapter} is now available at https://cosmicscans.com/tower-of-god-chapter-{new_chapter}/',
                'url': f'https://cosmicscans.com/tower-of-god-chapter-{new_chapter}/'
            }
            return push
        return None
# create an instance
scraper = TowerOfGodScraper()
