import json
import os
import requests

from django.forms.models import model_to_dict
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import render

import pandas as pd

from things.models import Thing
from dashboard.models import Record

from .dyno import query

import env_vars

WEATHER_APP_KEY = os.environ.get('WEATHER_APP_KEY', 'No value set')

@login_required(redirect_field_name=None, login_url='/')
def dashboard(request):
    things = Thing.objects.filter(user=request.user).all()
    thing_names = [thing.thing_name for thing in things]
    latest_ts = 0
    try:
        latest_ts = Record.objects.latest('timestamp')
    except ObjectDoesNotExist as not_exist:
        print("The Query did not return any values.")
    local_data ={}
    records = query(thing_names, latest_ts)
    #print(records[0])
    data = extract_needed_data(records, latest_ts)
    local_data = get_aggregates(thing_names)
    weather = get_weather()
    return render(request, 'dashboard.html', {'dashboard_data': {'data': json.dumps(local_data)}, 
                                              'weather_data': {'data': json.dumps(weather)}})


def get_aggregates(thing_names):
    aggregates = Record.objects.filter(thing_name__in=thing_names).values()
    df = pd.DataFrame().from_dict(aggregates)
    df = df.groupby([pd.Grouper(key='iso_timestamp', freq='15min'), pd.Grouper('thing_name')]).mean().dropna()
    df.reset_index(inplace=True)
    df['iso_timestamp'] = df['iso_timestamp'].astype(str)
    df['iso_timestamp'] = df['iso_timestamp'].str[:16]
    return df.to_dict()

def get_weather():
    resp = requests.get('https://api.openweathermap.org/data/2.5/onecall?lat=53.3244431&lon=-6.3857854&appid=%s' % WEATHER_APP_KEY)
    print(resp.status_code)
    if resp.status_code == 200:
        return resp.json()
    return {}

def extract_needed_data(records, latest_ts):
    for record in records:
        row = get_record(record, latest_ts)
        c = 0
        if row:
            Record.objects.create(**row)
            c += 1
        print(str(c) + " new records added.")

def get_record(record, latest_ts):
    if latest_ts > int(record.get('timestamp')):
        print(1)
        return None
    if not record.get('data'):
        print(2)
        return None
    if not record['data'].get('metadata'):
        print(3)
        return None
    data = record['data'].get('state')
    print(data)
    if not data.get('desired'):
        print(4)
        return None
    if not data['desired'].get('data'):
        print(5)
        return None

    return {
        'thing_name': record.get('deviceId'),
        'timestamp': int(record.get('timestamp') or 0),
        'iso_timestamp': data['desired'].get('timestamp'),
        'illuminance': float(data['desired'].get('data').get('illuminance') or 0),
        'temperature': float(data['desired'].get('data').get('temperature') or 0),
        'humidity': float(data['desired'].get('data').get('humidity') or 0),
        'soil_probe': int(data['desired'].get('data').get('soil_probe') or 0) ,
    }
