from django.conf.urls import patterns, url
from control import views

urlpatterns = patterns('',
    url(r'^play/$', views.play, name='play'),
    url(r'^stop/$', views.stop, name='stop'),
    url(r'^currentStation/$', views.current_station, name='current_station'),
    url(r'^volume/$', views.volume, name='volume'),
    url(r'^remove/$', views.remove, name='remove'),
    url(r'^add/$', views.add, name='add'),
    url(r'^move/$', views.move, name='move'),
    url(r'^radioState/$', views.radio_state, name='radio_state'),

    url(r'^$', views.index, name='index'),
)

