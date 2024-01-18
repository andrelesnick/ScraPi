# Template for scraper sources

import json, random
from fake_useragent import UserAgent

from datetime import datetime, timedelta

# read email and password from config.json
# with open('config.json', 'r') as f:
#     config = json.load(f)
#     email = config['email']
#     password = config['password']

class Scraper:
    def __init__(self):
        self.check_again = datetime.now() # time to check again
        self.filename = 'filename'
        self.name = 'Proper Name'
        self.description = "A description of the source."
        self.data = {}
        self.frequency = 10
        self.enabled = True # Whether or not the scraper is active
        self.has_image = False
        self.image_url = False
        self.ua = UserAgent()


        # self.urgent_frequency = None
        # self.urgent_days = None
        
        # self.email = email
        # self.password = password

    @property
    def headers(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
            "Mozilla/5.0 (iPad; CPU OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/86.0.4240.93 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
            # "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
            # "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Android 10; Mobile; LG-M255; rv:91.0) Gecko/91.0 Firefox/91.0"
        ]

        return {'User-Agent': random.choice(user_agents)}
    
    def get_storage(self):
        # get json file, if it exists
        try:
            with open('sources/'+self.filename + '.json', 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            print("No storage file found for", self.filename +", creating one...")

        

    def save_storage(self):
        with open('sources/'+self.filename + '.json', 'w') as f:
            json.dump(self.data, f, indent=4)

    # Returns scraped data if updated, None otherwise
    def scrape_data(self):
        pass
        # Check if element has updated
        # If not, then return None
        # Else, gather necessary stuff, modify data, and return email content

    def update_check(self):
        adjustment = 1 + (random.uniform(-0.10, 0.15))
        freq = self.frequency * adjustment
        self.check_again = datetime.now() + timedelta(minutes=freq)
    
        






