from django.http import HttpResponse
from django.shortcuts import render
import json
import string
from control.backend import Backend

def index(request):
    return render(request, template_name='index.html')

# -------- State --------------------------------------------------------------
def radio_state(request):
    response = Backend.Instance().get_state()
    return HttpResponse(json.dumps(response), mimetype="application/json")


# -------- Play ---------------------------------------------------------------
def play(request):
    backend = Backend.Instance()
    backend.play()
    state = backend.get_state()
    return HttpResponse(json.dumps(state), mimetype="application/json")


# -------- Stop ---------------------------------------------------------------
def stop(request):
    Backend.Instance().stop()
    return HttpResponse(status=200)


# -------- Station ------------------------------------------------------------
def current_station(request):
    station = Backend.Instance().get_current_station()
    return HttpResponse(json.dumps(station), mimetype="application/json")


# -------- Station List--------------------------------------------------------
def station_list(request):
    station_list = Backend.Instance().get_station_list()
    return HttpResponse(json.dumps(station_list), mimetype="application/json")

def update_station_list(request):
    if request.method == "POST":
        station_list = json.loads(request.raw_post_data)
        Backend.Instance().write_stations(station_list)
        return HttpResponse(status=200)
    return HttpResponse(status=400)


# -------- Volume -------------------------------------------------------------
def volume(request):
    volume = Backend.Instance().get_volume()
    return HttpResponse(json.dumps(volume), mimetype="application/json")
