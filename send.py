#!/usr/bin/env python
from __future__ import unicode_literals
import json
import calendar
import datetime
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
        self.server.ehlo()
        self.server.starttls()
        self.server.login(self.server_config['email'], self.server_config['password'])

    def send_message(self, to_address, message):
        self.server.sendmail(self.server_config['email'], to_address, message)

    def close_server(self):
        self.server.quit()


def load_json_config():
    with open('config/config.json') as configFile:
        global config
        config = json.load(configFile)
        if not (config):
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
    month = calendar.month_name[now.month + 1]  # next month

    for person in renters:
        print("notifying {0} for ${1}".format(person['name'], person['amount']))
        venmo_link = VENMO_DEEPLINK.format(config['recipient'], person['amount'], month, now.year)

        message_to_send = MESSAGE.format(person['name'], person['amount'], venmo_link)
        try:
            client.send_message(person['phone'], message_to_send)
        except Exception, e:
            client.send_message('justin.simonelli@gmail.com', str(e))

    client.close_server()

    print("notifications complete!")

    return None


notify()
