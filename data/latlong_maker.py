"""This file is intended for one-time use: to get geocodes into the database, not for server queries.  
That may change if other Bibliocommons libraries are added."""

import os
import sys
import requests

# Local imports
from model import Branch, db, connect_to_db

# Parent imports
sys.path.append("../")
from server import app

# Setup: database connection, api key, branches, 
GEOCODE_KEY = os.environ['GOOGLE_GEOCODE_API_KEY']
API_URL = "https://maps.googleapis.com/maps/api/geocode/json"
connect_to_db(app)

library_branches = Branch.query.all()
geocode_data = []

for branch in library_branches:
    response = requests.get(API_URL, {'address': branch.address, 'key': GEOCODE_KEY})
    if response.status_code != 200:
        print response.url
    else:
        data = response.json()
        latlong = data['results'][0]['geometry']['location']
        branch.latitude = latlong['lat']
        branch.longitude = latlong['lng']
db.session.commit()