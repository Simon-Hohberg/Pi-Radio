from control.singleton import Singleton
from threading import Lock
from control.controls import Controls, ControlsThread
import control.utils as utils
import os
import re
import subprocess as sub

FNULL = open(os.devnull, 'w')
VOLUME_REGEX = re.compile('Front\sLeft:\sPlayback\s\d+\s\[(\d?\d?\d)%')
STATIONS_FILE = 'stations.radio'

@Singleton
class Backend():
    '''
    This is the singleton backend that is in charge of implementing the actual
    input effects like switching the station, changing the volume. Also, starts
    a ControlsThread for reading the inputs.
    '''
    
    
    def __init__(self):
        self.mpc_lock = Lock()
        self.station_file_lock = Lock()
        self.noise_lock = Lock()
        self.amixer_lock = Lock()
        self.noise_process = None
        self.offline = False
        
        # check internet connection
        packet_loss = utils.check_inet_connection()
        
        if packet_loss == 100:
            self.offline = True
        
        # read stations from file
        self.stations = self.read_stations(STATIONS_FILE)
        
        # when online create mpc playlist, otherwise do not load stations, since
        # m3u resolution would fail, instead create ad-hoc network to all 
        # configuration
        if not self.offline:
            self.load_stations(self.stations)
        else:
            print('No internet connection. Setting up ad-hoc network.')
            utils.setup_ad_hoc()
        
        # create controls model and thread for reading input 
        self.controls = Controls()
        self.controls.set_update_callback(self.update)
        controls_thread = ControlsThread(self.controls)
        controls_thread.start()
        
        # start the radio when online
        if not self.offline:
            self.play()
    
    
    def load_stations(self, stations):
        '''
        Creates a mpc playlist with the given stations. First the current mpc
        playlist is cleared, then the new stations are added. Tries to resolve
        m3u URIs automatically.
        Thread safe, requires mpc_lock.
        @param stations: Stations for new mps playlist 
        '''
        # > lock
        self.mpc_lock.acquire()
        
        # clear playlist
        sub.call(['mpc', 'clear'])
        # add all stations from stations file
        for s in stations:
            uri = s[1]
            # mpc cannot handle m3u, workaround: parsing the m3u and using first
            # uri in list
            if uri.endswith('.m3u'):
                try:
                    uri = utils.resolve_m3u(uri)
                    sub.call(['mpc', 'add', uri])
                except ValueError:
                    print('Cannot resolve m3u: ' + s[1] + ' for ' + s[0] + '. Station is not added.')
            else:
                sub.call(['mpc', 'add', uri])
        
        # < release
        self.mpc_lock.release()
    
    
    def read_stations(self, stations_file_name):
        '''
        Reads a list of stations from the given file. Each line in the file has
        to have the form: "<readable station name>,<station uri>".
        Thread safe, requires station_file_lock
        @param stations_file_name: Name of the file to read stations from
        @return: List of tuples: [ (<readable station name>, <station uri>), 
        ... ]
        '''
        # > lock
        self.station_file_lock.acquire()
        
        try:
            stations_file = open(stations_file_name, 'r')
            station_list = []
            # expecting csv station file (Station Name,URI)
            for line in stations_file:
                splitted = line.split(',')
                station_list.append((splitted[0].strip(), splitted[1].strip()))
            stations_file.close()
        except IOError:
            station_list = []
        
        # < release
        self.station_file_lock.release()
        
        return station_list
    
    
    def write_stations(self, station_list, stations_file_name):
        '''
        Writes the list of tuples to the file with given name. List has to 
        contain tuples like (<readable station name>, <station uri>). The tuples
        will be written CSV like, one line for each tuple: "<readable station
        name>,<station uri>". Overwrites old file.
        Thread safe, requires "station_file_lock"
        @param station_list: List of tuples with station name and URI to be 
        written
        @param stations_file_name: Name of the file to write to
        '''
        self.stations = station_list
        # > lock
        self.station_file_lock.acquire()
        
        # creates file, overwrites old file
        stations_file = open(stations_file_name, 'w+')
        for station in station_list:
            stations_file.write(station[0] + ',' + station[1] + '\n')
        stations_file.close();
        
        # < release
        self.station_file_lock.release()
    
    
    def get_station_list(self):
        '''
        Returns the list of stations. Each station is represented by a tuple:
        (<readable station name>, <station uri>).
        @return: List of tuple, one tuple for each station with name and URI 
        '''
        return self.stations
    
    
    def update(self):
        '''
        Callback for control updates, i.e. change of station, volume or audio 
        source. The actual effect of a control input is realized here.
        Thread safe, requires controls object's lock
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
        '''
        Switches to the given station. Switching to the same station as the 
        current should be avoided.
        Thread safe, requires "noise_lock" and "mpc_lock"
        @param new_station: Index of the station to switch to. Station 0 is 
        noise. Real stations start at 1.
        '''
        print 'switching to station: ' + str(new_station)
        # station 0 plays noise
        if new_station == 0:
            self.stop()
            # > lock
            self.noise_lock.acquire()
            # kill already running process, should not be the case
            if self.noise_process is not None:
                self.noise_process.kill()
            # start new process playing noise
            self.noise_process = sub.Popen(['play', 'radio-noise.ogg', 'repeat'])
            # < release
            self.noise_lock.release()
        else:
            # stop running noise process
            if self.noise_process is not None:
                # > lock
                self.noise_lock.acquire()
                self.noise_process.kill()
                self.noise_process = None
                # < release
                self.noise_lock.release()
            # > lock
            self.mpc_lock.acquire()
            # switch to new station
            sub.call(['mpc', 'play', str(new_station)], stdout=FNULL)
            # < release
            self.mpc_lock.release()
    
    
    def play(self, lock_controls=True):
        '''
        Starts playing the current station, i.e. current station from controls
        object.
        Thread safe, requires controls object's lock
        @param lock_controls: optional, when set to False will not lock 
        controls, default is True
        '''
        # > lock
        if lock_controls:
            self.controls.lock.acquire()
        
        self.switch_station(self.controls.station)
        
        # < release
        if lock_controls:
            self.controls.lock.release()
    
    
    # -------- State ----------------------------------------------------------
    def get_state(self):
        '''
        Get the volume and currently selected (not necessarily playing) station.
        Calls thread safe methods, only.
        @return: Dictionary with keys 'volume' and 'station'
        '''
        volume = self.get_volume()
        station = self.get_current_station()
        return dict(volume=volume, station=station)
    
    
    # -------- Stop -----------------------------------------------------------
    def stop(self):
        '''
        Stops the radio.
        Thread safe, requires "mpc_lock"
        '''
        # > lock
        self.mpc_lock.acquire()
        sub.call(['mpc', 'stop'], stdout=FNULL)
        # < release
        self.mpc_lock.release()
    
    
    # -------- Volume ---------------------------------------------------------
    def set_volume(self, new_volume):
        '''
        Set new volume through amixer.
        Thread safe, requires "amixer_lock"
        @param new_volume: New volume in percent (0 -> silence, 100 -> as loud 
        as it gets)
        '''
        # > lock
        self.amixer_lock.acquire()
        sub.call(['amixer', '-c', '0', 'sset', 'Headphone', str(new_volume) + '%'], stdout=FNULL)
        # < release
        self.amixer_lock.release()
    
    
    def get_volume(self):
        '''
        Get the current volume through amixer.
        Thread safe, requires "amixer_lock"
        @return: Current volume in percent
        '''
        # > lock
        self.amixer_lock.acquire()
        amixer = sub.check_output(['amixer', '-c', '0', 'sget', 'Headphone'])
        # < release
        self.amixer_lock.release()
        volume = VOLUME_REGEX.findall(amixer)[0]
        return volume
    
    
    # -------- Audio Source ---------------------------------------------------
    def set_ext_audio_source(self, use_external):
        '''
        Switches between external audio source and internal. External means 
        using the microphones playback for ouput with amixer.
        Thread safe, requires "amixer_lock"
        @param use_external: When True the audio source plugged to the 
        microphone jack is looped through to be played, otherwise it is muted.
        '''
        # > lock
        self.amixer_lock.acquire()
        if use_external:
            self.stop()
            sub.call(['amixer', 'sset', 'Mic', 'Playback', 'unmute'])
        else:
            sub.call(['amixer', 'sset', 'Mic', 'mute'])
            self.play(lock_controls=False)
        # < release
        self.amixer_lock.release()
    
    
    # -------- Station --------------------------------------------------------
    def get_current_station(self):
        '''
        Get the currently playing station from mpc.
        Thread safe, requires "mpc_lock"
        @return: Currently playing station
        '''
        self.mpc_lock.acquire()
        mpc = sub.check_output(['mpc', 'current'])
        station = mpc.strip()
        self.mpc_lock.release()
        return station
