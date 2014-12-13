import subprocess as sub
import re

PACKET_LOSS_REGEX = re.compile('(\d)%\spacket\sloss')
URI_REGEX = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

AD_HOC_NAME = 'PI-RADIO'
AD_HOC_ADDR = '192.168.1.222'
AD_HOC_CONF = [ 'iface wlan0 inet static\n',
                '\taddress ' + AD_HOC_ADDR + '\n',
                '\tnetmask 255.255.255.0\n',
                '\twireless-channel 1\n',
                '\twireless-essid ' + AD_HOC_NAME + '\n',
                '\twireless-mode ad-hoc\n' ]


def check_inet_connection():
    '''
    Tries to ping fff.org three times with an overall timeout of five seconds
    and returns the percentaged packet loss. If there is no connection at all
    100 is returned.
    @return: Percentaged packet loss for three pings
    '''
    # try to quietly ping fff.org three times with a deadline of 5s
    try:
        ping_output = sub.check_output(['ping', '-q', '-c', '3', '-w', '5', 'example.org'])
    except sub.CalledProcessError:
        return 100
    # get packet loss in %
    packet_loss = PACKET_LOSS_REGEX.findall(ping_output)
    # when there is no connection at all "unknown host" is returned, so the
    # regex won't find anything
    if len(packet_loss) > 0:
        packet_loss = int(packet_loss[0])
    else:
        packet_loss = 100
    return packet_loss


def resolve_m3u(m3u):
    '''
    Tries to resolve the given m3u by parsing its output and taking the first
    URI. This URI is then returned.
    @param m3u: A URI ending with .m3u that should be resolved
    @raise ValueError: When resolving fails
    @return: The first URI in the m3u
    '''
    m3u_data = sub.check_output(['curl', m3u])
    uris = URI_REGEX.findall(m3u_data)
    if len(uris) > 0:
        return uris[0]
    else:
        raise ValueError()


def setup_ad_hoc():
    sub.call(['ifdown', 'wlan0'])
    
    ifaces_file = open('/etc/network/interfaces', 'r')
    ifaces_data = ifaces_file.readlines()
    print ifaces_data
    
    # remove old configuration
    start_line_idx = ifaces_data.index('iface wlan0 inet static\n')
    current_line = ifaces_data[start_line_idx]
    while len(current_line.strip()) > 0:
        ifaces_data.remove(current_line)
        current_line = ifaces_data[start_line_idx]
    
    # add new ad-hoc configuration
    offset = 0
    for line in AD_HOC_CONF:
        ifaces_data.insert(start_line_idx + offset, line)
        offset += 1
    
    ifaces_file = open('/etc/network/interfaces', 'w')
    ifaces_file.writelines(ifaces_data)
    
    sub.call(['ifup', 'wlan0'])


def say(text):
    sub.call('espeak -a 150 -s 120 "' + text + '" --stdout | aplay')
