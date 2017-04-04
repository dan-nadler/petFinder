from datetime import datetime, timedelta
import pytz
from local_settings import *
import petfinder
import email

api = petfinder.PetFinderClient(api_key=api_key, api_secret=api_secret)

pets = []
names = []
for pet in api.shelter_getpets(id=shelter_id, status='A', output='full'):
    if pet['lastUpdate'] > datetime.now().replace(tzinfo=pytz.timezone('America/New_York')) - timedelta(minutes=120):
        if not pet['name'] in names:
            names.append(pet['name'])

            temp = {}
            temp['name'] = pet['name']
            temp['age'] = pet['age']
            temp['breeds'] = pet['breeds']
            temp['mix'] = pet['mix']
            temp['size'] = pet['size']
            temp['id'] = pet['id']
            temp['photo'] = pet['photos'][0]['url']

            pets.append(temp)
            del temp
        else:
            break

print(pets)
