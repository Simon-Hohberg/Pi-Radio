from django.conf.urls import patterns, url
from control import views

urlpatterns = patterns('',
    url(r'^play/$', views.play, name='play'),
    url(r'^stop/$', views.stop, name='stop'),
    url(r'^currentStation/$', views.current_station, name='current_station'),
    url(r'^volume/$', views.volume, name='volume'),
    url(r'^radioState/$', views.radio_state, name='radio_state'),
    url(r'^updateStationList/$', views.update_station_list, name='update_station_list'),
    url(r'^stationList/$', views.get_station_list, name='get_station_list'),

    url(r'^$', views.index, name='index'),
)

