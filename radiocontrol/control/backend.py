from multiprocessing.connection import Listener
from array import array
from control.singleton import Singleton
from threading import Lock
from control.controls import Controls, ControlsThread
import os

@Singleton
class Backend():
    
    def __init__(self):
        
        self.mpc_lock = Lock()
        self.station_file_lock = Lock()
        
        self.stations = self.read_stations()

	for s in self.stations:
            os.system('mpc add ' + s[1])
        
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
                station_list.append((splitted[0], splitted[1]))
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
        if new_station == 0:
            # TODO: play noise
            True;
        else:
            # > lock
            self.mpc_lock.acquire()
            mpc = os.popen("mpc play " + str(new_station))
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
        os.system("mpc stop")
        # < release
        self.mpc_lock.release()
    
    
    # -------- Volume ---------------------------------------------------------
    def set_volume(self, new_volume):
        self.mpc_lock.acquire()
        os.system("amixer set Headphone " + str(new_volume) + "%")
        self.mpc_lock.release()
    
    def get_volume(self):
        self.mpc_lock.acquire()
        mpc = os.popen("mpc volume")
        volume = mpc.read().replace("volume:", "").strip()
        self.mpc_lock.release()
        return volume
    
    
    # -------- Audio Source ---------------------------------------------------
    def set_ext_audio_source(self, use_external):
        if use_external:
            # TODO:
            True;
        else:
            # TODO:
            True;
    
    
    # -------- Station --------------------------------------------------------
    def get_current_station(self):
        self.mpc_lock.acquire()
        mpc = os.popen("mpc current")
        station = mpc.read().strip()
        self.mpc_lock.release()
        return station
