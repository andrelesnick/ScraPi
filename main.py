from bs4 import BeautifulSoup as bs
from datetime import datetime
import time
import requests
import traceback

# todo: add command line arguments just to run certain scrapers

import os, json
import importlib
import smtplib, ssl
from email.message import EmailMessage

# Note: if you need to reset email password, go to https://myaccount.google.com/apppasswords
with open('config.json', 'r') as f:
    config = json.load(f)
    sender = config['sender']
    receiver = config['receiver']
    password = config['password']
    pushbullet_token = config['pushbullet_token']
    image_uploaded = config['image_uploaded']

def write_config():
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    
# list to hold all scraper instances
scrapers = []

# directory containing all source files
source_dir = './sources'

# get a list of all python files in the source directory
source_files = [f for f in os.listdir(source_dir) if f.endswith('.py')]

# loop through all source files
for source_file in source_files:
    if source_file == '__init__.py' or source_file == 'Scraper.py':
        continue
    # remove .py from file name to get module name
    module_name = source_file[:-3]

    # import module from sources subpackage
    module = importlib.import_module(f'sources.{module_name}')

    # get scraper instance and add to list
    scrapers.append(module.scraper)

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_image(scraper):
    if scraper.filename in config['image_uploaded']:
        return config['image_uploaded'][scraper.filename]
    elif not scraper.image_url:
        return None
    
    # image exists, but not uploaded yet
    print("Need to create image/channel for " + scraper.filename)
    headers = {
        'Access-Token': pushbullet_token,
        'Content-Type': 'application/json'
    }

    data = {
        'file_name': scraper.filename+'.png',
        'file_type': 'image/png',
        'file_url': scraper.image_url
    }

    response = requests.post('https://api.pushbullet.com/v2/upload-request', headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        data = response.json()

        # upload file using image from images/
        with open('images/'+scraper.filename+'.png', 'rb') as f:
            files = {'file': (scraper.filename+'.png', f, data['file_type'])}
            response = requests.post(data['upload_url'], files=files)
            if response.status_code == 204:
                # print(f'Image for {scraper.filename} sent successfully.')

                # now create channel
                data['channel_tag'] = scraper.filename
                data['channel_name'] = scraper.name
                data['channel_description'] = scraper.description

                request_data = {
                    'tag': data['channel_tag'],
                    'name': data['channel_name'],
                    'description': data['channel_description'],
                    'image_url': data['file_url'],
                    'website_url': 'https://github.com/andrelesnick/ScraPi',
                    'subscribe': True
                }

                response = requests.post('https://api.pushbullet.com/v2/channels', headers=headers, data=json.dumps(request_data))

                if response.status_code == 204:
                    config['image_uploaded'][scraper.filename] = data # channel tag = filename
                    write_config()
                    return data
                else:
                    print(f'Error in creating channel for {scraper.filename}:', response.text)
                    print("status:", response.status_code)
                    print("Request:", request_data, headers)
                    return None
            else:
                print(f'Error in uploading image for {scraper.filename}:', response.text)
                return None

        return data
    else:
        print(f'Error in requesting image upload for {scraper.filename}:', response.text)
        return None
def send_email(email_content):
    # email is a dictionary with keys 'subject'/'title' and 'plaintext'/'html'
    msg = MIMEMultipart('alternative')
    
    # add your plain text version here
    text = f"{email_content['plaintext']}\n\nSent by ScraPi"
    part1 = MIMEText(text, 'plain')
    
    # create the HTML version
    html = f"""
    <html>
    <body>
        {email_content['html']}
        <p style="font-size: 0.8em; color: #777;">Sent by ScraPi</p>
    </body>
    </html>
    """
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)
    
    msg['Subject'] = email_content['subject'] 
    msg['From'] = sender
    msg['To'] = receiver

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(sender, password)
        server.send_message(msg, from_addr=sender, to_addrs=receiver)
        print("Email sent successfully.")

def send_push(push_content, scraper):
    # image = get_image(scraper)
    

    headers = {
        'Access-Token': pushbullet_token,
        'Content-Type': 'application/json'
    }

    data = {
        'type': 'note',
        'title': push_content['title'],
        'body': push_content['body'],
        # 'url': push_content['url'],
        'channel_tag': scraper.filename
    }

    # if image:
        # data['file_name'] = image['file_name']
        # data['file_url'] = image['file_url']
        # push_content['file_width'] = image['width']
        # push_content['file_height'] = image['height']
        # data['image_width'] = 100
        # data['image_height'] =  100
        # data['file_type'] = image['file_type']
        
    response = requests.post('https://api.pushbullet.com/v2/pushes', headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        print('Push sent successfully.')
    else:
        print('Error in sending push:', response.text)

def send_notification(notification_content, scraper):
    if notification_content['type'] == 'email':
        send_email(notification_content)
    elif notification_content['type'] == 'push':
        send_push(notification_content, scraper)


## todo: when going through each scraper, sleep until minimum(check_again)
## todo: include execution statistics, just log time before and after scrape

## todo: if request error, skip and try again next time
while True:
    # loop through all scrapers
    for scraper in scrapers:
        if not scraper.enabled:
            if datetime.now() >= scraper.check_again:
                print(f"  Skipped {scraper.filename} at {datetime.now().strftime('%H:%M:%S')}")
        # check if it's time to scrape
        elif datetime.now() >= scraper.check_again:
            # scrape data
            try:
                notification_content = scraper.scrape_data()
            except Exception as e:
                print('Error in scraping data for', scraper.filename, 'at', datetime.now().strftime('%H:%M:%S'), '\n\n')
                tb = traceback.format_exc()
            else:
                tb = False
            finally:
                if tb:
                    print(tb, '\n\n')
                    scraper.enabled = False
                    scraper.update_check()
                    exception_html = f"""
        <div style="border: 1px solid #999; border-radius: 5px; padding: 10px; background-color: #f8d7da; color: #721c24;">
            <h2 style="margin-top: 0; color: #721c24;">Error Occurred:</h2>
            <pre style="white-space: pre-line; font-family: monospace;">{str(tb)}</pre>
        </div>
        """
                    send_email({
                        'type': 'email',
                        'subject': 'Error in scraping data for ' + scraper.filename,
                        'plaintext': str(tb),
                        'html': exception_html
                    })
                    continue
            # if email content was returned, send email, save storage
            if notification_content:
                print('Update for ' + scraper.filename + ' found! Sending notification...')
                send_notification(notification_content, scraper)
                scraper.save_storage() # scrapers might save storage in between 
            # update check_again time
            scraper.update_check()
            print(f"Scraped {scraper.filename} at {datetime.now().strftime('%H:%M:%S')}")
    
    # pause for a bit to prevent excessive resource use
    time.sleep(15)  # wait before next round


