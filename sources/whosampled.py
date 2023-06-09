import time
from bs4 import BeautifulSoup as bs
import requests
import re

import datetime
from .Scraper import Scraper

class WhoSampledScraper(Scraper):
    def __init__(self): # filename defaults to empty string if not provided
        super().__init__()
        self.filename = 'whosampled'
        self.frequency = 60
        self.check_again = datetime.datetime.now() + datetime.timedelta(minutes=10) # Making this 10 minutes to prevent unnecessary spam whenever I need to test
        # self.urgent_frequency = 5
        # self.urgent_days = 6
        self.data = {
            'artists': ['Caravan Palace', 'Tor'], # used for easy way to add artists manually
            'artist_data': {
                    'Nujabes': [{
                        'title': 'Aruarian Dance',
                        'url': 'https://www.whosampled.com/Nujabes/Aruarian-Dance/',
                        'samples': 3
                    }
                    ]
            }
        }
        self.get_storage()

    def scrape_data(self):
        new_samples = {}
        for artist_ in self.data['artists']:    
            artist = artist_.replace(' ', '-')
            url = artist
            if not 'whosampled.com' in artist:
              url = f'https://www.whosampled.com/{artist}/' # artist can be either name or url
            url += 'samples/'
            parts = url.split(".com", 1)
            base_url = parts[0] + ".com"
            start_url = parts[1]
        

            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            soup = bs(response.text, 'lxml')
            # with open("output.html", "w", encoding='utf-8') as file:
            #     file.write(soup.prettify())

            artist_name_element = soup.select_one('div.artistDetails > h1')
            artist_name = artist_name_element.text.strip() if artist_name_element else "Unknown Artist"
            samples_element = soup.find('span', {'class': 'section-header-title'})
            # Extract the number of samples from the text of the element
            samples_text = samples_element.text if samples_element else "0 samples found"
            num_samples_new = int(re.search(r'\d+', samples_text).group())

            tracks_current = self.data['artist_data'].get(artist_name, [])
            num_samples_current = sum(track['samples'] for track in tracks_current)
            num_new = num_samples_new - num_samples_current
            body = str(num_new) + f' new sample(s) found for {artist_name}!'
            if num_samples_new > num_samples_current:
                print(body)
            else:
                continue
            
            # new samples found, so determine them
            def extract_info_from_page(soup):
                tracks = soup.find_all('article', attrs={'itemprop': 'track'})
                artist_track_info = []
                # print("tracks:", tracks)
                for track in tracks:
                    track_title = track.find('span', attrs={'itemprop': 'name'}).text
                    track_url = base_url + track.find('a', attrs={'itemprop': 'url'})['href']

                    samples = track.find_all('li')
                    sample_count = len(samples)

                    # If there is "See more samples" text, extract the number and add it to the count
                    more_samples = track.find('a', text=re.compile(r'^See \d+ more sample$'))
                    if more_samples is not None:
                        more_samples_count = int(re.search(r'\d+', more_samples.text).group())
                        sample_count += more_samples_count

                    artist_track_info.append({
                        'title': track_title,
                        'url': track_url,
                        'samples': sample_count
                    })
                print("extracting, artist track info:", artist_track_info)
                return artist_track_info

            # find URLs of new samples
            def find_new_samples(old_data, new_data):
                old_data_dict = {track['title']: track for track in old_data}
                new_samples = []

                for new_track in new_data:
                    old_track = old_data_dict.get(new_track['title'])
                    if old_track is None or new_track['samples'] > old_track['samples']:
                        new_samples.append(new_track)

                return new_samples

            all_artist_track_info = []
            current_page_url = start_url

            page_artist_track_info = extract_info_from_page(soup)
            all_artist_track_info.extend(page_artist_track_info)

            has_next_button = True
            next_button = soup.find('span', {'class': 'next'})
            if next_button is None:  # No more pages
                has_next_button = False
            else:  # Get URL of next page
                current_page_url = next_button.find('a')['href']

            while has_next_button:
                time.sleep(2)
                response = requests.get(base_url+current_page_url, headers=self.headers)
                response.raise_for_status()

                soup = bs(response.text, 'lxml')
                
                page_artist_track_info = extract_info_from_page(soup)
                all_artist_track_info.extend(page_artist_track_info)

                next_button = soup.find('span', {'class': 'next'})
                if next_button is None:  # No more pages
                    has_next_button = False
                else:  # Get URL of next page
                    current_page_url = next_button.find('a')['href']
            # print(tracks_current)
            # print(all_artist_track_info)
            print('current artist:' + artist_name)
            new_samples[artist_name] = find_new_samples(tracks_current, all_artist_track_info)
            self.data['artist_data'][artist_name] = all_artist_track_info

        # Done going through all artists
        # print("new samples:", new_samples)

        def generate_html(data):
            html_string = '<div style="font-family: Arial, sans-serif;">'
            
            for artist in data:
                artist_name = artist
                tracks = data[artist_name]  # Get artist's tracks
                html_string += f'<h2>{artist_name}</h2>'
                html_string += '<table style="width: 100%; border-collapse: collapse;">'
                html_string += '<tr style="background-color: #f8f8f8;">' \
                            '<th style="border: 1px solid #ddd; padding: 8px;">Track Title</th>' \
                            '<th style="border: 1px solid #ddd; padding: 8px;">Number of Samples</th>' \
                            '</tr>'
                for track in tracks:
                    html_string += '<tr>' \
                                f'<td style="border: 1px solid #ddd; padding: 8px;"><a href="{track["url"]}">{track["title"]}</a></td>' \
                                f'<td style="border: 1px solid #ddd; padding: 8px;">{track["samples"]}</td>' \
                                '</tr>'
                html_string += '</table><br>'
                    
            html_string += '</div>'
            return html_string

        return {
            'type': 'email',
            'subject': 'New Sample(s) Found!',
            'plaintext': str(new_samples),
            'html': generate_html(new_samples)
        }
        
               
# create an instance
scraper = WhoSampledScraper()
