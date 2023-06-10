from bs4 import BeautifulSoup as bs
from datetime import datetime
import time
import requests

# todo: add command line arguments just to run certain scrapers

import os, json
import importlib
import smtplib, ssl
from email.message import EmailMessage

with open('config.json', 'r') as f:
    config = json.load(f)
    sender = config['sender']
    receiver = config['receiver']
    password = config['password']
    pushbullet_token = config['pushbullet_token']
    
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

def send_push(push_content):
    headers = {
        'Access-Token': pushbullet_token,
        'Content-Type': 'application/json'
    }

    data = {
        'type': 'link',
        'title': push_content['title'],
        'body': push_content['body'],
        'url': push_content['url']
    }

    response = requests.post('https://api.pushbullet.com/v2/pushes', headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        print('Push sent successfully.')
    else:
        print('Error in sending push:', response.text)

def send_notification(notification_content):
    if notification_content['type'] == 'email':
        send_email(notification_content)
    elif notification_content['type'] == 'push':
        send_push(notification_content)


## todo: when going through each scraper, sleep until minimum(check_again)
## todo: include execution statistics, just log time before and after scrape

## todo: if request error, skip and try again next time
while True:
    # loop through all scrapers
    for scraper in scrapers:
        # check if it's time to scrape
        if datetime.now() >= scraper.check_again:
            # scrape data
            try:
                notification_content = scraper.scrape_data()
            except Exception as e:
                print('Error in scraping data for', scraper.filename, 'at', datetime.now().strftime('%H:%M:%S'), '\n\n')
                print(e, '\n\n')
                exception_html = f"""
    <div style="border: 1px solid #999; border-radius: 5px; padding: 10px; background-color: #f8d7da; color: #721c24;">
        <h2 style="margin-top: 0; color: #721c24;">Error Occurred:</h2>
        <pre style="white-space: pre-line; font-family: monospace;">{str(e)}</pre>
    </div>
    """
                send_email({
                    'type': 'email',
                    'subject': 'Error in scraping data for ' + scraper.filename,
                    'plaintext': str(e),
                    'html': exception_html
                })
                break
            # if email content was returned, send email, save storage
            if notification_content:
                print('Update for ' + scraper.filename + ' found! Sending notification...')
                send_notification(notification_content)
                scraper.save_storage()
            # update check_again time
            scraper.update_check()
            print(f"Scraped {scraper.filename} at {datetime.now().strftime('%H:%M:%S')}")
    
    # pause for a bit to prevent excessive resource use
    time.sleep(15)  # wait before next round
