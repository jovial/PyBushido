import sys
import time
import struct

from ant.core import driver
from ant.core import node
from ant.core import event
from ant.core import message
from ant.core.constants import *

from bushido import send_message, partial_compare_list


import Pyro4
import atexit
import datetime as dt

import thread
import threading

import time
import injector


NETKEY = '\x00\x00\x00\x00\x00\x00\x00\x00'

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()

class InputThread(threading.Thread):

    def __init__(self,incoming,outgoing):
        threading.Thread.__init__(self)    
        self.incoming = incoming
        self.outgoing = outgoing

    def run(self):
        while True:
            ch = getch()
            if ch == 'i':
                self.incoming.toggle()
                print 'toggling, incoming current: ', self.incoming.closed
            elif ch == 'o':
                self.outgoing.toggle()
                print 'toggling, outgoing current: ', self.outgoing.closed            
            elif ch == 'q':
                raise KeyboardInterrupt
                break
            time.sleep(0.001)

class BushidoForwarderListener(event.EventCallback):

    def __init__(self, incomining_channel, retransmit_channel):
        self.incomining_channel = incomining_channel
        self.retransmit_channel = retransmit_channel
        self.closed = False
        
    def close(self):
        self.closed = True
        
    def toggle(self):
        if not self.closed:
            self.closed = True
        else:
            self.closed = False

    def process(self, msg):
        
        # make remove listener method on channel
        if self.closed:
            return
        try:
            if isinstance(msg,message.ChannelBroadcastDataMessage) or isinstance(msg,message.ChannelAcknowledgedDataMessage) or isinstance(msg,message.ChannelBurstDataMessage):
                msg = self.injectData(msg)
                self.retransmit_channel.send(msg)
                #print msg
            time.sleep(0.001)
            
        except Exception, e:
            if isinstance(e,KeyboardInterrupt):
                raise KeyboardInterrupt
            import traceback
            traceback.print_exc()
            #print e
    
    def extractData(self,msg):
        data = msg.getRawData()
        data = struct.unpack('B' * len(data), data)
        return data
    
    def repackMsg(self,msg,data):
        args = ['B' * 8]
        args.extend(data)
        new_packed = struct.pack(*args)
        msg.setRawData(new_packed)
        return msg
            
    def injectData(self,msg):
        return msg
            
class BushidoReceiveListener(BushidoForwarderListener):
    def injectData(self,msg):
        data = self.extractData(msg)
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            data = list(data)
            injector.injectReceive(data)
            msg = self.repackMsg(msg,data)
        return msg
 
class BushidoTransmitListener(BushidoForwarderListener):
    def injectData(self,msg):
        data = self.extractData(msg)
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            data = list(data)
            injector.injectTransmit(data)
            msg = self.repackMsg(msg,data)
        return msg           

class BushidoBrakeForwarder(object):
    def __init__(self):
        self.daemon = Pyro4.core.Daemon()
              
    def exit(self):
        print 'exiting'
        self.brake_listener.close()
        self.retransmit_listener.close()
        self.closeChannel(self.brake_channel)
        self.closeChannel(self.retransmit_channel)
        
    def closeChannel(self,channel):
        channel.close()
        channel.unassign()
    
    def assignBrakeChannel(self, antnode):
            key = node.NetworkKey('N:ANT+', NETKEY)
            antnode.setNetworkKey(0, key)
            channel = antnode.getFreeChannel()
            channel.name = 'C:BUSHIDO_BRAKE'
            channel.assign('N:ANT+', CHANNEL_TYPE_TWOWAY_RECEIVE)
            channel.setID(0x51, 4302, 1)
            channel.setSearchTimeout(TIMEOUT_NEVER)
            channel.setPeriod(4096)
            channel.setFrequency(60)
            channel.open()
            self.brake_channel = channel
            
    def assignRetransmitChannel(self, antnode):
            key = node.NetworkKey('N:ANT+', NETKEY)
            antnode.setNetworkKey(0, key)
            channel = antnode.getFreeChannel()
            channel.name = 'C:BUSHIDO_HEADUNIT'
            channel.assign('N:ANT+', CHANNEL_TYPE_TWOWAY_TRANSMIT)
            channel.setID(0x51, 0x1234, 1)
            channel.setSearchTimeout(TIMEOUT_NEVER)
            channel.setPeriod(4096)
            channel.setFrequency(60)
            channel.open()
            self.retransmit_channel = channel
            
    
    def start(self):
        antnode= Pyro4.core.Proxy("PYRONAME:pyant.server")
        antnode2 = Pyro4.core.Proxy("PYRONAME:pyant.server2")
        
        self.assignRetransmitChannel(antnode2)
        self.assignBrakeChannel(antnode)
        self.brake_listener = BushidoReceiveListener(self.brake_channel,self.retransmit_channel)
        self.daemon.register(self.brake_listener)
        self.brake_channel.registerCallback(self.brake_listener)
        
        self.retransmit_listener = BushidoTransmitListener(self.retransmit_channel,self.brake_channel)
        self.daemon.register(self.retransmit_listener)
        self.retransmit_channel.registerCallback(self.retransmit_listener)
        
        atexit.register(self.exit)
        
        incoming = self.brake_listener
        outgoing = self.retransmit_listener
        
        input_thread = InputThread(incoming,outgoing)
        input_thread.start()
        
        #thread.start_new_thread(getInput, ())
               

        self.daemon.requestLoop()
        
        
if __name__ == "__main__":
    forwarder = BushidoBrakeForwarder()
    forwarder.start()