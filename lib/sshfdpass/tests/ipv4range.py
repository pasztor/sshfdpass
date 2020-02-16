'''
sshfdpass.tests.ipv4range
-------------------------

This specific test finds out if our local ip address is falls into one specific address range.
Since portability was one of the most important objective during the development, I tried to not do any OS-specific solution here.
The actual sulution: The test has two parameters: dsthost and dstport.
It establishes a tcp socket connecting to the dsthost and dstport, than gets the local socket of the connection using the getsockname() method.
The default to connect to is 8.8.8.8:53.
If you don't want to reveal yourself with these attempts, you might want to override this in the settings, like this:
    settings:
        tests:
            ipv4range:
                dsthost: 1.2.3.4
                dstport: 80
Target of this test is a list if IPv4 networks in cidr notation.
If the local ip is within any of the targets, then the test evaluates as true.
Otherwise it evaluates as false.

Intended usage as a base test for tests, like this:
    tests:
        lan:
            ipv4range:
                - 192.168.0.0/24
                - 10.1.2.0/24
'''

import sshfdpass.common
log = sshfdpass.common.log
import sshfdpass.tests
import socket

# Stackoverflow: https://stackoverflow.com/questions/819355/how-can-i-check-if-an-ip-is-in-a-network-in-python
# Answer 9, addressInNetwork -> ip_in_range
def ip_in_range(ip, net):
    '''Helper function to decide if an ip address is within a cidr-defined range or not.

    This solution on stackoverflow seemed pretty portable and nice looking, so I imported here as a helper function

    Parameters
    ----------
    ip: str
        The IP address what we want to check
    net: str
        The network in cidr notation which the ip address should be checked if it's inside.

    Returns
    -------
    bool
        Returns a bool if the IP address is in the given net.
    '''
    ipaddr = int(''.join([ '%02x' % int(x) for x in ip.split('.') ]), 16)
    netstr, bits = net.split('/')
    netaddr = int(''.join([ '%02x' % int(x) for x in netstr.split('.') ]), 16)
    mask = (0xffffffff << (32 - int(bits))) & 0xffffffff
    log.message('debug','ip_in_range check(%s, %s): %s'%(ip, net, str(bool((ipaddr & mask) == (netaddr & mask)))))
    return (ipaddr & mask) == (netaddr & mask)

class Test(sshfdpass.tests.AbstractTest):
    '''
    ipv4range test class

    About the puprose, see the module's doc.

    Since it's based on the AbstractTest class, we have not to much to do here.
    Only the _defaults and the _evaluate have to be redefined here.

    Attributes
    ----------
        nothing specific. Just the inherited ones

    Methods
    -------
    myip(self):
        Gives back the local IP address, used to access to the given dsthost:dstport.
        I added this as a method of the object, so it can use the object's cache
        attribute to store the result.
        If the local address is found once, than it don't have to be guessed again
        upon re-evaluation.
    _defaults(self):
        returns {'dsthost': '8.8.8.8', 'dstport': 53}
    _evaluate(self, **kwargs):
        checks if myip() is inside any of the given targets.
    '''
    def _defaults(self):
        return dict(dsthost='8.8.8.8', dstport=53)

    @property
    def myip(self):
        '''simport property getter, detailed description in the Test class' methods'''
        if self.cache.get('myip') == None:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            s.connect((self.settings.get('dsthost'), self.settings.get('dstport')))
            myip , myport = s.getsockname()
            s.close()
            self.cache['myip'] = myip
            return myip
        else:
            return self.cache.get('myip')

    def _evaluate(self, **kwargs):
        settings=dict()
        settings.update(self.settings)
        settings.update(**kwargs)
        myip = self.myip
        for i in settings.get('target',[]):
            if ip_in_range(myip, i):
                return True
        return False
