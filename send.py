#!/usr/bin/env python
from __future__ import unicode_literals
import json
import calendar
import datetime
import requests
import smtplib

config = None
SMTP_GMAIL = "smtp.gmail.com"
SMTP_GMAIL_PORT = 587

MESSAGE = """{0}! ${1} this month\'s for rent, thx!
{2}"""

VENMO_DEEPLINK = "venmo://paycharge?txn=pay&recipients={0}&amount={1}&note={2}%20{3}%20Rent"


class MessageClient(object):
    def __init__(self):

        self.server_config = config['gmail']
        self.server = smtplib.SMTP(SMTP_GMAIL, SMTP_GMAIL_PORT)
        self.server.starttls()
        self.server.login(self.server_config['email'], self.server_config['password'])
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': config['shortener']['key']
        }

    def shorten(self, url):
        values = {
                "domain": config['shortener']['domain'],
                "originalURL": url,
          }

        r = requests.post('https://api.short.cm/links', data=json.dumps(values), headers=self.headers)

        if not(r):
            raise Exception("Unable to call url shortener!")

        response = r.json()

        url = "http://" + config['shortener']['domain'] + "/" + response['path']

        return url


    def send_message(self, to_address, message):
        self.server.sendmail(self.server_config['email'], to_address, message)

    def close_server(self):
        self.server.quit()


def load_json_config():
    with open('config/config.json') as configFile:
        global config
        config = json.load(configFile)
        if not(config):
            raise Exception('Unable to read config file!')

def get_renters():

    renters = config['renters']
    if not (renters):
        raise Exception('Cannot read renters json file!')
    return renters


def notify():
    print("notify(): running..")
    load_json_config()
    renters = get_renters()
    client = MessageClient()

    now = datetime.datetime.now()
    month = calendar.month_name[now.month]

    for person in renters:
        print("notifying {0} for ${1}".format(person['name'], person['amount']))
        venmo_link = VENMO_DEEPLINK.format(config['recipient'], person['amount'], month, now.year)
        shorty = client.shorten(venmo_link)

        message_to_send = MESSAGE.format(person['name'], person['amount'], venmo_link)
        client.send_message(person['phone'], message_to_send)

    client.close_server()

    print("notifications complete!")

    return None

notify()
