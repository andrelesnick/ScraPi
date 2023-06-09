# Template for scraper sources

import json, random

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
        self.data = {}
        self.frequency = 10
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
            }
        # self.urgent_frequency = None
        # self.urgent_days = None
        
        # self.email = email
        # self.password = password

    def get_storage(self):
        try:
            with open('sources/'+self.filename + '.json', 'r') as f:
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
    
        






