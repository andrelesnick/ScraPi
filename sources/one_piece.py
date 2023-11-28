import time
from bs4 import BeautifulSoup as bs
import requests
import re

from .Scraper import Scraper

class OnePieceScraper(Scraper):
    def __init__(self): # filename defaults to empty string if not provided
        super().__init__()
        self.filename = 'one_piece'
        self.name = 'One Piece'
        self.description = 'Receive updates when new chapters of One Piece are released.'
        self.frequency = 5
        self.has_image = True
        self.image_url = 'https://i.imgur.com/zUnC8yH.png' # do NOT include in push, only for config
        # self.urgent_frequency = 5
        # self.urgent_days = 6
        self.data = {
            'latest_chapter': 1085,
        }
        self.get_storage()

    def scrape_data(self):
        url = 'https://tcbscans.com/'  # The URL of the website where chapters are listed
        response = requests.get(url, headers=self.headers)

        # Parse the HTML content
        soup = bs(response.text, 'lxml')

        # Find all elements containing the term "One Piece Chapter"
        # Assuming these are found in <a> tags, you can adjust this as per your requirement.
        elements = soup.find_all('a', text=re.compile(r"One Piece Chapter (\d+)",re.IGNORECASE))
        # print(elements)
        if elements is None or len(elements) == 0:
            print("Couldn't find any One Piece chapters.")
            # write soup response to file
            with open('one_piece.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            return

        # Extract the chapter numbers from the elements' text and find the max
        chapter_numbers = [int(re.search(r"One Piece Chapter (\d+)", el.text).group(1)) for el in elements]
        latest_online_chapter = max(chapter_numbers)

        if latest_online_chapter > self.data['latest_chapter']:
            self.data['latest_chapter'] = latest_online_chapter
            push_url = 'https://tcbscans.com/chapters/7389/one-piece-chapter-'+str(latest_online_chapter)
            return {
                'type': 'push',
                'title': self.name,
                'body': f'Chapter {latest_online_chapter} is now available at {push_url}',
                'url': push_url,
            }
        else:
            return None
# create an instance
scraper = OnePieceScraper()
