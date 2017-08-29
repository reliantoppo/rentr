#!/usr/bin/env python
from __future__ import unicode_literals
import json
import calendar
import datetime
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

config = None
SMTP_GMAIL = "smtp.gmail.com"
SMTP_GMAIL_PORT = 587

MESSAGE = """{0}! ${1} for this month\'s for rent, thx!
{2}"""

HTML_MESSAGE = "<html><body>{0}</body></html>"

STATUS_MESSAGE = "Here are the notification statues for {0} {1}<br/>{2}"

STATUS_LINE_ITEM = "<p {0}><strong>{1} - ${2}</strong></p>"

VENMO_DEEPLINK = "venmo://paycharge?txn=pay&recipients={0}&amount={1}&note={2}%20{3}%20Rent%20&Internet"


class MessageClient(object):
    def __init__(self):
        self.server_config = config['gmail']
        self.server = smtplib.SMTP(SMTP_GMAIL, SMTP_GMAIL_PORT)
        self.server.ehlo()
        self.server.starttls()
        self.server.login(self.server_config['email'], self.server_config['password'])

    def notify(self, to_address, message):
        self.server.sendmail(self.server_config['email'], to_address, message)

    def close(self):
        self.server.quit()


def load_json_config():
    with open('config/config.json') as configFile:
        global config
        config = json.load(configFile)
        if not (config):
            raise Exception('Unable to read config file!')


def get_renters():
    renters = config['renters']
    if not renters:
        raise Exception('Cannot read renters json file!')
    return renters


def notify():
    print("notify(): running..")
    load_json_config()
    renters = get_renters()
    status_msg = ""
    status_success = "style=\"color:#85db2e\""
    status_error = "style=\"color:#fb0f0f\""
    client = MessageClient()

    now = datetime.datetime.now()
    month = calendar.month_name[now.month + 1]  # next month

    for person in renters:
        name = person['name']
        amount = person['amount']
        phone = person['phone']
        recipient = config['recipient']
        admin_email = config['admin_email']

        print("notifying {0} for ${1}".format(name, amount))

        venmo_link = VENMO_DEEPLINK.format(recipient, amount, month, now.year)
        message_to_send = MESSAGE.format(name, amount, venmo_link)

        try:
            client.notify(phone, message_to_send)
            status_msg += STATUS_LINE_ITEM.format(status_success, name, amount)
        except Exception, e:
            status_msg += STATUS_LINE_ITEM.format(status_error, name, amount)

    complete_msgs = STATUS_MESSAGE.format(month, now.year, status_msg)
    email = MIMEMultipart('alternative')
    email['Subject'] = "Rentr Notification Statuses - {} {}\n\n".format(month, now.year)
    content = HTML_MESSAGE.format(complete_msgs)
    mime_html = MIMEText(content, 'html')
    email.attach(mime_html)

    client.notify(admin_email, email.as_string())
    client.close()

    print("notifications complete!")

    return None


notify()
