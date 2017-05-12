import subprocess as subp
import re

def pingtest(ip, interface):
    """
    pingtest checks whether the IP is reachable on the given
    interface using a single ICMP ping.

    :param ip: The IP address to ping
    :param interface: The interface to use as the origin for the ping
    :return: True on success
    
    """
    response = subp.call(['ping', '-I', interface, ip, '-c', '1'])

    if response == 0:
        return True
    return False

def pingtest_hard(ip, interface, test_class):
    """
    pingtest_hard checks whether the IP is reachable on the given
    interface using a single ICMP ping. Same as pingtest, but throws
    exception on fail.

    :param ip: The IP address to ping
    :param interface: The interface to use as the origin for the ping
    :param test_class: The origin Test class from which the function
                       was called
    """
    success = pingtest(ip, interface)
    if success == False:
       test_class.fail("Ping on interface {0} to ip {1} failed".format(interface, ip));

def get_known():
    """
    Returns a list of known (existing) networks in the system
    
    :return: The list of known networks
    
    """
    return subp.Popen(['nmcli', '-t', '--fields', 'NAME,UUID,ACTIVE,TYPE', 'c'], stdout=subp.PIPE, stderr=subp.PIPE)

def connect(ssid, password):
    """ 
    Connects to a ssid, based on whether it exists.
    if it doesn't, makes a new connection, otherwise
    uses the existing
    
    :param ssid: The ssid to connect to
    :param password: The password of the AP to connect to
    
    """ 
    knownNetworks = get_known()

    stdout, stderr = knownNetworks.communicate()

    # each connection is seperated by '\n'
    connectionList = stdout.split("\n")
    existing = False

    """ 
    we check for the existance of the ssid in the known networks
    if the network ssid is found, it will connect using its UUID
    if not found, a new connection will be created and connected to
    """
    for con in connectionList:
        cParts = con.split(":") # nmcli -t output is seperated by :
        # see if the ssid exist, and has the correct type
        if ssid in cParts and cParts[3] == "802-11-wireless":
           existing = True
           if cParts[2] != "yes": # yes means active => don't reconnect
              subp.call(['nmcli', 'con', 'up', 'uuid', cParts[1]]) # cParts[1] contains uuid

    # when the network does not yet exist, create a new one
    if existing == False:
        switch = subp.call(['nmcli', 'dev', 'wifi', 'con', ssid, 'password', password])   

def get_gateway(interface, test_class):
    """
    Gets the default gateway of the given interface
    
    :param interface: The interface on which to get
    :param test_class: The class to fail when something goes wrong
    :return: String of gateway
    
    """
    # get the default gateway by parsing ip route's output
    gatewayP1 = subp.Popen(['ip', 'route', 'show', 'dev', interface], stdout=subp.PIPE, stderr=subp.PIPE).communicate()[0]
    gatewayMatches = re.search(r'^default\s+via\s+(?P<gw>[^\s]*)\s', gatewayP1, re.MULTILINE)
    
    if gatewayMatches == None
        test_class.fail("Getting gateway failed")
    gateway = gatewayMatches.group(1)
    
    return gateway
