import logging
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText

import petfinder
import pytz
from flask import Flask

from local_settings import *


def find_new_pets():
    api = petfinder.PetFinderClient(api_key=api_key, api_secret=api_secret)

    pets = []
    names = []
    for pet in api.shelter_getpets(id=shelter_id, status='A', output='full'):
        logging.debug(
            '{0}: {1} vs {2}'.format(pet['name'], pet['lastUpdate'].isoformat(), datetime.utcnow().isoformat()))
        if not pet['name'] in names:
            names.append(pet['name'])
            if pet['lastUpdate'] > datetime.utcnow().replace(tzinfo=pytz.timezone('UTC')) - timedelta(minutes=15):
                temp = {}

                temp['name'] = pet['name']
                temp['age'] = pet['age']
                temp['breeds'] = pet['breeds']
                temp['mix'] = pet['mix']
                temp['size'] = pet['size']
                temp['id'] = pet['id']
                temp['photo'] = pet['photos'][0]['url']
                temp['updated'] = pet['lastUpdate']
                pets.append(temp)

                logging.info('saved')
                del temp
        else:
            break
    return pets


def send_email(to, pets):
    from_addr = EMAIL['USERNAME']
    password = EMAIL['PASSWORD']

    text = '<html><head></head><body>'
    for pet in pets:
        text += '<p>'
        text += '<h1>%s</h1>' % pet['name']
        text += '<img src=\'%s\'/>' % pet['photo']
        text += '<ul>'
        text += '<li>Listing updated: %s</li>' % pet['updated'].strftime('%m/%d/%Y %I:%M %p')
        text += '<li>Age: %s</li>' % str(pet['age'])
        text += '<li>Size: %s</li>' % pet['size']
        text += '<li>Link: https://www.petfinder.com/petdetail/%s</li>' % pet['id']
        text += '</ul>'
        text += '</p>'
    text += '</body></html>'

    msg = MIMEText(text, 'html')
    msg['Subject'] = 'petfinder Update!'
    msg['From'] = from_addr
    msg['To'] = to

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(from_addr, password)
    server.sendmail(from_addr, to, msg.as_string())
    server.quit()


def check_pets():
    logging.debug('Looking for new pets.')
    pets = find_new_pets()
    logging.debug('Found %i pets' % len(pets))
    if len(pets) > 0:
        logging.debug('Sending email')
        send_email('gdaniels313@gmail.com', pets)
        send_email('dnadler87@gmail.com', pets)


app = Flask(__name__)


@app.route('/')
def home():
    return 'Hello, World. This is the petfinder finder!'
