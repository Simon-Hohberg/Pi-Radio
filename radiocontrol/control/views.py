from django.http import HttpResponse
from django.shortcuts import render
import os
import json
import string

def index(request):
    return render(request, template_name='index.html')

def radio_state(request):
    volume = get_volume()
    station = get_current_station()
    response = dict(volume=volume, station=station)
    return HttpResponse(json.dumps(response), mimetype="application/json")


def play(request):
    mpc = os.popen("mpc play")
    state = mpc.read()
    return HttpResponse(json.dumps(state), mimetype="application/json")

def stop(request):
    os.system("mpc stop")
    return HttpResponse(status=200)


def current_station(request):
    station = get_current_station()
    return HttpResponse(json.dumps(station), mimetype="application/json")

def get_current_station():
    mpc = os.popen("mpc current")
    station = mpc.read().strip()
    return station


def get_station_list(request):
    try:
        stations_file = open("stations.radio", "r")
        station_list = map(str.strip, list(stations_file))
        stations_file.close()
    except IOError:
        station_list = []
    return HttpResponse(json.dumps(station_list), mimetype="application/json")

def update_station_list(request):
    if request.method == "POST":
        station_list = json.loads(request.raw_post_data)
        # creates file, overwrites old file
        stations_file = open("stations.radio", "w+")
        for station in station_list:
            stations_file.write(station + "\n")
        stations_file.close();
        return HttpResponse(status=200)
    return HttpResponse(status=400)


def volume(request):
    volume = get_volume()
    return HttpResponse(json.dumps(volume), mimetype="application/json")

def get_volume():
    mpc = os.popen("mpc volume")
    volume = mpc.read().replace("volume:", "").strip()
    return volume


def remove(request):
    # TODO
    return HttpResponse(status=400)

def add(request):
    # TODO
    return HttpResponse(status=400)

def move(request):
    # TODO
    return HttpResponse(status=400)

