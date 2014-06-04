from multiprocessing.connection import Listener
from array import array
from controls import Controls, ControlsThread

def start():
    controls = Controls()
    controls_thread = ControlsThread(controls)
    controls_thread.run()
    
    address = ('localhost', 6000)  # family is deduced to be 'AF_INET'
    listener = Listener(address, authkey='p1-r4d10')
    conn = listener.accept()
    print 'connection accepted from', listener.last_accepted
    while True:
        msg = conn.recv()
        
        # do something with msg
        if msg == 'close':
            conn.close()
            break
    listener.close()
