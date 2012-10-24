"""
Extending on demo-03, implements an event callback we can use to process the
incoming data.

"""

import sys
import time
import struct

from ant.core import driver
from ant.core import node
from ant.core import event
from ant.core import message
from ant.core.constants import *

#from config import *

import Pyro4
import atexit

NETKEY = '\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'

#channel = None


def exit():
    print 'exiting'
    antnode.stop()

class NodeProxy(object):

    def __init__(self,node,daemon):
        self.node = node
        self.daemon = daemon
        for channel in self.node.channels:
            self.daemon.register(channel)
        self.daemon.register(self.node.driver)        

    def start(self):
        self.node.start()

    def stop(self, reset=True):
        self.node.stop(reset=reset)

    def reset(self):
        self.node.reset()

    def init(self):
        self.node.init()
       
    def getCapabilities(self):
        return self.node.getCapabilities()

    def setNetworkKey(self, number, key=None):
        self.node.setNetworkKey(number,key=key)

    def getNetworkKey(self, name):
        return self.node.getNetworkKey(name)

    def getFreeChannel(self):
        channel = self.node.getFreeChannel()
        return channel

    def getChannels(self):
        channels = self.node.channels
        return channels
                
    def registerEventListener(self, callback):
        self.node.registerEventListener(callback)

    def process(self, msg):
        self.node.process(msg)

    def getDriver(self):
        return self.node.driver

    def send(self,msg):
        self.node.send(msg)


# A run-the-mill event listener
class HRMListener(event.EventCallback):
    def process(self, msg):
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            print 'Heart Rate:', ord(msg.payload[8])
            #msg = message.ChannelRequestMessage(message_id=MESSAGE_CHANNEL_ID)

            #channel.node.driver.write(msg.encode()) 
            #try:
            #    print len(msg.payload)
            #    print type(msg.payload)
            #    test = struct.unpack('BBBBBBBBB',msg.payload)
           # except Exception, e:
            #    print e
            #print test
            #print 'hi'
            #for i in range(0,8):
            #    print ord(msg.payload[i])

# Initialize
#stick = driver.USB2Driver(SERIAL, log=LOG, debug=DEBUG)
stick = driver.USB2Driver('usb0',number=0)
antnode = node.Node(stick)
antnode.start()

atexit.register(exit)

# Setup channel
#key = node.NetworkKey('N:ANT+', NETKEY)
#antnode.setNetworkKey(0, key)
#channel = antnode.getFreeChannel()
#channel.name = 'C:HRM'
#channel.assign('N:ANT+', CHANNEL_TYPE_TWOWAY_RECEIVE)
#channel.setID(120, 0, 0)
#channel.setSearchTimeout(TIMEOUT_NEVER)
#channel.setPeriod(8070)
#channel.setFrequency(57)
#channel.open()

with Pyro4.core.Daemon() as daemon:
    with Pyro4.naming.locateNS() as ns:
        node = NodeProxy(antnode,daemon)
        uri = daemon.register(node)
        ns.register("pyant.server",uri)
    daemon.requestLoop()


# Setup callback
# Note: We could also register an event listener for non-channel events by
# calling registerEventListener() on antnode rather than channel.
#channel.registerCallback(HRMListener())

# Wait
#print "Listening for HR monitor events (120 seconds)..."
#time.sleep(240)

# Shutdown
#channel.close()
#channel.unassign()
#antnode.stop()
