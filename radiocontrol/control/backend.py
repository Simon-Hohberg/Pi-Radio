from multiprocessing.connection import Listener
from array import array
from control.singleton import Singleton
from threading import Lock
from control.controls import Controls, ControlsThread
import os
import re
import subprocess as sub

FNULL = open(os.devnull, 'w')
VOLUME_REGEX = re.compile('Front\sLeft:\sPlayback\s\d+\s\[(\d?\d?\d)%')
URI_REGEX = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

@Singleton
class Backend():
    
    def __init__(self):
        
        self.mpc_lock = Lock()
        self.station_file_lock = Lock()
        self.noise_lock = Lock()
        self.amixer_lock = Lock()
        self.noise_process = None
        self.stations = self.read_stations()
        
        # clear playlist
        sub.call(['mpc', 'clear'])
        # add all stations from stations file
        for s in self.stations:
            uri = s[1]
            # mpc cannot handle m3u, workaround: parsing the m3u and using first
            # uri in list
            if uri.endswith('.m3u'):
                m3u_data = sub.check_output(['curl', uri])
                uri = URI_REGEX.findall(m3u_data)[0]
            sub.call(['mpc', 'add', uri])
        
        # create controls and thread for interfacing
        self.controls = Controls()
        self.controls.set_update_callback(self.update)
        
        controls_thread = ControlsThread(self.controls)
        controls_thread.start()
        
        # start the radio
        self.play()
    
    
    def read_stations(self):
        # > lock
        self.station_file_lock.acquire()
        
        try:
            stations_file = open('stations.radio', 'r')
            station_list = []
            # expecting csv station file (Station Name,URL)
            for line in stations_file:
                splitted = line.split(',')
                station_list.append((splitted[0].strip(), splitted[1].strip()))
            stations_file.close()
        except IOError:
            station_list = []
        
        # < release
        self.station_file_lock.release()
        
        return station_list
    
    
    def write_stations(self, station_list):
        self.stations = station_list
        # > lock
        self.station_file_lock.acquire()
        
        # creates file, overwrites old file
        stations_file = open('stations.radio', 'w+')
        for station in station_list:
            stations_file.write(station[0] + ',' + station[1] + '\n')
        stations_file.close();
        
        # < release
        self.station_file_lock.release()
    
    
    def get_station_list(self):
        return self.stations
    
    
    def update(self):
        '''
        Called when the controls of the radio change, i.e. station, volume, 
        audio source switch.
        '''
        # > lock
        self.controls.lock.acquire()
        
        if self.controls.station_updated:
            self.switch_station(self.controls.station)
        if self.controls.volume_updated:
            self.set_volume(self.controls.volume)
        if self.controls.ext_as_updated:
            self.set_ext_audio_source(self.controls.ext_audio_source)
        
        # < release
        self.controls.lock.release()
    
    
    # -------- Play -----------------------------------------------------------
    def switch_station(self, new_station):
        print 'switching to station: ' + str(new_station)
        if new_station == 0:
            self.stop()
            # > lock
            self.noise_lock.acquire()
            self.noise_process = sub.Popen(['play', 'radio-noise.ogg', 'repeat'])
            # < release
            self.noise_lock.release()
        else:
            if self.noise_process is not None:
                # > lock
                self.noise_lock.acquire()
                self.noise_process.kill()
                self.noise_process = None
                # < release
                self.noise_lock.release()
            # > lock
            self.mpc_lock.acquire()
            sub.call(['mpc', 'play', str(new_station)], stdout=FNULL)
            # < release
            self.mpc_lock.release()
    
    
    def play(self):
        # > lock
        self.controls.lock.acquire()
        self.switch_station(self.controls.station)
        # < release
        self.controls.lock.release()
    
    
    # -------- State ----------------------------------------------------------
    def get_state(self):
        volume = self.get_volume()
        station = self.get_current_station()
        return dict(volume=volume, station=station)
    
    
    # -------- Stop -----------------------------------------------------------
    def stop(self):
        # > lock
        self.mpc_lock.acquire()
        sub.call(['mpc', 'stop'], stdout=FNULL)
        # < release
        self.mpc_lock.release()
    
    
    # -------- Volume ---------------------------------------------------------
    def set_volume(self, new_volume):
        # > lock
        self.amixer_lock.acquire()
        sub.call(['amixer', '-c', '0', 'sset', 'Headphone', str(new_volume) + '%'], stdout=FNULL)
        # < release
        self.amixer_lock.release()
    
    
    def get_volume(self):
        # > lock
        self.amixer_lock.acquire()
        amixer = sub.check_output(['amixer', '-c', '0', 'sget', 'Headphone'])
        # < release
        self.amixer_lock.release()
        volume = VOLUME_REGEX.findall(amixer)[0]
        return volume
    
    
    # -------- Audio Source ---------------------------------------------------
    def set_ext_audio_source(self, use_external):
        # > lock
        self.amixer_lock.acquire()
        if use_external:
            self.stop()
            sub.call(['amixer', 'sset', 'Mic', 'Playback', 'unmute'])
        else:
            sub.call(['amixer', 'sset', 'Mic', 'mute'])
            self.play()
        # < release
        self.amixer_lock.release()
    
    
    # -------- Station --------------------------------------------------------
    def get_current_station(self):
        self.mpc_lock.acquire()
        mpc = sub.check_output(['mpc', 'current'])
        station = mpc.strip()
        self.mpc_lock.release()
        return station
