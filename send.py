#!/usr/bin/env python

from __future__ import unicode_literals

from twilio.rest import TwilioRestClient
import logging
import json
import requests

logger = logging.getLogger(__name__)

MESSAGE = """Hey {0}! It's that time again, time to pay rent. You owe ${1} this month. Pay with the link below, thanks!

{2}
"""

VENMO_DEEPLINK = "venmo://paycharge?txn=pay&audience=friends&recipients=justinsims&amount={0}&note=Rent"

GOOGLE_SHORTENER = "https://www.googleapis.com/urlshortener/v1/url?key={0}"

NOT_CONFIGURED_MESSAGE = """Cannot initialize Twilio notification
middleware. Required enviroment variables TWILIO_ACCOUNT_SID, or
TWILIO_AUTH_TOKEN or TWILIO_NUMBER missing. Don't forget to bring the private directory over!"""


def load_renters_file():
    with open('config/renters.json') as rentersFile:
        renters = json.load(rentersFile)
        if not(renters):
            raise Exception('Cannot read renters json file!')
        return renters


def load_twilio_config():
    with open('config/private/twilio.json') as twilioFile:
        config = json.load(twilioFile);

        twilio_account_sid = config['TWILIO_ACCOUNT_SID']
        twilio_auth_token = config['TWILIO_AUTH_TOKEN']
        twilio_number = config['TWILIO_NUMBER']

        if not all([twilio_account_sid, twilio_auth_token, twilio_number]):
            logger.error(NOT_CONFIGURED_MESSAGE)
            raise Exception(NOT_CONFIGURED_MESSAGE)

        return (twilio_number, twilio_account_sid, twilio_auth_token)


class MessageClient(object):
    def __init__(self):
        (twilio_number, twilio_account_sid,
         twilio_auth_token) = load_twilio_config()

        self.twilio_number = twilio_number
        self.twilio_client = TwilioRestClient(twilio_account_sid,
                                              twilio_auth_token)

    def send_message(self, body, to):
        self.twilio_client.messages.create(body=body, to=to,
                                           from_=self.twilio_number
                                           # media_url=['https://demo.twilio.com/owl.png'])
                                           )
def notify_everyone():
    print("notify_everyone(): running..")

    renters = load_renters_file()
    client = MessageClient()

    for person in renters:
        print("notifying {0}...".format(person['name']))
        message_to_send = MESSAGE.format(person['name'], person['amount'], VENMO_DEEPLINK.format(person['amount']))
        #params = json.dumps({'longUrl': url_to_shorten})
        #response = requests.post(post_url, params, headers={'Content-Type': 'application/json'})

        client.send_message(message_to_send, person['phone_number'])

    print("notifications complete!")

    return None

notify_everyone();
