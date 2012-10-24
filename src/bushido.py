import sys
import time
import struct

from ant.core import driver
from ant.core import node
from ant.core import event
from ant.core import message
from ant.core.constants import *

import Pyro4
import atexit
import datetime as dt

import thread
import Queue

NETKEY = '\x00\x00\x00\x00\x00\x00\x00\x00'

#channel = None

#FIXME: lock channel for each channel.send() or is it thread safe ? check

# while recieving ad 01 etc send ac 03 04
# if ad 01 04 0a 00 00 0a 02 break


# ac 03 02 

# ad 01 03

#FIXME: is this needed? seems to work without?
def keep_alive(channel):
    while True:
            print 'sending keep alive'
            msg = message.ChannelBroadcastDataMessage()
            channel.send(msg)
            time.sleep(1)
        
# zero padded message
def send_message(channel, packet):
    msg = message.ChannelBroadcastDataMessage()
    new_data = [0] * 8
    new_data[:len(packet)] = packet
    args = ['B' * 8]
    args.extend(new_data)
    new_packed = struct.pack(*args)
    msg.setRawData(new_packed)
    channel.send(msg)
    #FIXME: move to thread calling this function?
    time.sleep(0.005)    
    


# not used anymore
#def init_generator(channel):
#    for i in range(0,30):
#        yield send_message(channel,[0xac,0x02])

    #for i in range(0,2):
    #    yield send_message(channel,[0xac,0x01])
#    for i in range(0,5):
#        yield send_message(channel,[0xac,0x12])
#    for i in range(0,5):
#        yield send_message(channel,[0xac,0x11])

#    yield thread.start_new_thread(keep_alive,(channel,))  

    #for i in range(0,3):
    #for i in range(0,3):
    #    yield send_message(channel,[0xac,0x03,0x04])            

  

def compare_list(a, b):
    return (len(a) == len(b) and all(a[i] == b[i] for i in range(len(a))))


def partial_compare_list(a, b):
    return all(a[i] == b[i] for i in range(len(a)))   

# this is for transmitting a message until a TX success recieved
# on tx sucesss call next() and use a thread to repeatably call the method: call
# improvement (is this necessary?) : add event flags, so that next only advances if recieves event flag matching that expected
class SlaveTransmitQueue(Queue.Queue):

    def __init__(self, *args, **kwargs):
        Queue.Queue.__init__(self, *args, **kwargs)
    
    def get(self):
        self.not_empty.acquire()
        try:
            while not self._qsize():
                self.not_empty.wait()
            return self.queue[0]
        finally:
            self.not_empty.release()    
    
    def next(self):
        return Queue.Queue.get(self, False)

    def call(self):
        function, args, kwargs = self.get()
        function(*args, **kwargs)
        
# ad 01 02  logging mode --- send dc01 dc02

## dd 10 02 increase slope

## dd 10 04 decrease slope


#FIXME: convert to class?
slave_transmit_queue = SlaveTransmitQueue()

# this is our function we run in a thread to repeatablly call SlaveTransmitQueue.call()
# see SlaveTransmitQueue for details
def slave_transmit():
    while True:
        # this blocks
        slave_transmit_queue.call() 


class CodeSequence(object):
    def __init__(self, sequence):
        self.code_sequence = sequence
        self.current_index = 0

    def next(self):
        value = self.code_sequence[self.current_index]
        self.current_index += 1
        if (self.current_index > (len(self.code_sequence) - 1)):
            self.current_index = 0
        return value
    

class BushidoData(object):
    
    def __init__(self):
        self.code_sequence = CodeSequence(['dc01', 'dc02'])
        self.slope = 0
               
    def getData(self):
        current = self.code_sequence.next()
        if current == 'dc01':
            return self.getDc01()
        elif current == 'dc02':
            return self.getDc02()

    def getDc01(self):
        data = [0xdc, 0x01, 0x00, 0x00, 0x00, 0x4d, 0x00, 0x00]
        data[3:5] = self.getSlopeBytes()      
        return data

    def getDc02(self):
        data = [0xdc, 0x02, 0x00, 0x99, 0x00, 0x00, 0x00, 0x00]     
        return data

    def getSlopeBytes(self):
        rtn = [0x00, 0x00]
        # send as slope * 10 ( max resolution 0.1?)
        slope = self.getSlope() * 10
        if slope < 0:
            rtn[0] = 0xff
            rtn[1] = 256 + slope
        else:
            rtn[1] = slope
        return rtn

    def increaseSlope(self, value=1):
        slope = self.getSlope()
        slope += value
        self.setSlope(slope)

    def decreaseSlope(self, value=1):
        slope = self.getSlope()
        slope -= value
        self.setSlope(slope)            

    def setSlope(self, value):
        if value > 20:
            value = 20
        if value < -5:
            value = -5
        print "slope: ",
        self.slope = value

    def getSlope(self):
        return self.slope


        

class BushidoListener(event.EventCallback):

    def __init__(self, logger, period, channel, transmit_queue):
        self.transmit_queue = transmit_queue
        self.logger = logger
        #self.init = init_generator(channel)
        #channel to respond on
        #self.init = None
        #self.send_connect = True
        #self.send_start = True
        self.channel = channel
        self.data = BushidoData()
        self.closed = False
        
    def close(self):
        self.closed = True

    def process(self, msg):
        
        # make remove listener method on channel
        if self.closed:
            return
        
        try:
            if isinstance(msg, message.ChannelBroadcastDataMessage):
                data = msg.getRawData()
                data = struct.unpack('B' * len(data), data)
                if (data[0] == 0xDD):
                    #Bushido data
                    if (data[1] == 0x01):   
                        time = dt.datetime.now()                     
                        #Packet format: dd01SSSSPPPPCCUU  P = Power, S = Speed, C = Cadence   
                        speed = ((data[2] << 8) + data[3]) / 16.1
                        power = (data[4] << 8) + data[5]
                        cadence = data[6]
                        self.logger.logSpeed(speed, time)
                        self.logger.logPower(power, time)
                        self.logger.logCadence(cadence, time)
                    if (data[1] == 0x02):
                        time = dt.datetime.now()
                        #Packet format: dd02DDDDDDDDHHUU  D = Distance, H = Heart Rate
                        distance = (data[2] << 24) + (data[3] << 16) + (data[4] << 8) + data[5]
                        heartRate = data[6]
                        self.logger.logDistance(distance, time)
                        self.logger.logHeartRate(heartRate, time)
                elif (data[0] == 0xad):
                    # bushido : 'i'm paused' 
                    if compare_list(data, [0xad , 0x01 , 0x03 , 0x0a , 0x00 , 0x00, 0x0a, 0x02]):
                        print 'pause detected'
                        send_message(self.channel, [0xac, 0x03, 0x02])
                    
                    # request data
                    elif partial_compare_list([0xad , 0x01 , 0x02], data):
                        payload = self.data.getData()
                        send_message(self.channel, payload)
                        import time
                        time.sleep(0.5)
                                                                           
                    #elif self.send_connect:
                        #pass
                        #send_message(self.channel,[0xac,0x03,0x04])

            elif isinstance(msg, message.ChannelAcknowledgedDataMessage):
                data = msg.getRawData()
                data = struct.unpack('B' * len(data), data)
                if partial_compare_list([0xdd, 0x10, 0x02], data):
                    print 'increasing slope'
                    self.data.increaseSlope()

                elif partial_compare_list([0xdd, 0x10, 0x04], data):
                    print 'decreasing slope'
                    self.data.decreaseSlope()
                            

            elif isinstance(msg, message.ChannelEventMessage):
                if msg.getMessageID() == 0x01 and msg.getMessageCode() == 0x03 :
                    try: 
                        self.transmit_queue.next() 
                    except:
                        pass                        
                    #if self.init:
                    #    try:
                            #print 'init next'
                    #        self.init.next()
                    #    except Exception, e:
                    #        print e
                    #        #print 'end init'
                    #        self.init = None
        except Exception, e:
            print e 
                
class Bushido(object):
    def __init__(self, logger, period):
        self.listener = None #BushidoListener(logger,period)
        self.daemon = Pyro4.core.Daemon()
        self.logger = logger
        self.logger_period = period
              
#TODO: git of sleeps - wait for channel event tx sucess
    def exit(self):
        print 'exiting'
        self.listener.close()
        time.sleep(5)
        #send_message(self.channel, [0xac, 0x03, 0x01])
        time.sleep(5)
        # terminate connection
        send_message(self.channel, [0xac, 0x03])
        time.sleep(5)
        self.channel.close()
        self.channel.unassign()
        

    def startCycling(self):
        slave_transmit_queue.put((send_message,[self.channel,[0xac,0x03,0x03]],{}))
               
        
    def initConnection(self):
        slave_transmit_queue.put((send_message, [self.channel, [0xac, 0x03, 0x04]], {}))
    
    def start(self):
        with Pyro4.core.Proxy("PYRONAME:pyant.server") as antnode:
            
            key = node.NetworkKey('N:ANT+', NETKEY)
            antnode.setNetworkKey(0, key)
            channel = antnode.getFreeChannel()
            channel.name = 'C:BUSHIDO'
            channel.assign('N:ANT+', CHANNEL_TYPE_TWOWAY_RECEIVE)
            channel.setID(0x52, 0, 0)
            channel.setSearchTimeout(TIMEOUT_NEVER)
            channel.setPeriod(4096)
            channel.setFrequency(60)
            channel.open()

            #for i in init_generator(channel):
            #    pass  

            transmit_queue = slave_transmit_queue          

            self.listener = BushidoListener(self.logger, self.logger_period, channel, transmit_queue)
            self.daemon.register(self.listener)
            channel.registerCallback(self.listener)

            self.channel = channel
            atexit.register(self.exit)

            time.sleep(2)
            
            self.initConnection()
            
            self.startCycling()
            
            #transmit_queue.put((send_message, [channel, [0xac, 0x02]], {}))
            #transmit_queue.put((send_message, [channel, [0xac, 0x12]], {}))
            #transmit_queue.put((send_message, [channel, [0xac, 0x11]], {}))

            #transmit_queue.put((send_message, [channel, [0xac, 0x03, 0x04]], {}))

            #transmit_queue.put((send_message, [channel, [0xac, 0x03, 0x01]], {}))
            
            
            #transmit_queue.put((send_message, [channel, [0xac, 0x03, 0x02]], {}))
            
            # start cycling flag
            #transmit_queue.put((send_message,[channel,[0xac,0x03,0x03]],{}))

            #transmit_queue.put((send_message, [channel, [0xdc, 0x01, 0x05, 0x07, 0x00, 0x50, 0x00, 0x00]], {}))

            #transmit_queue.put((send_message, [channel, [0xdc, 0x02, 0x00, 0x99, 0x00, 0x00, 0x00, 0x00]], {}))
            
            #transmit_queue.put((send_message, [channel, [0xdc, 0x0a]], {}))

            #transmit_queue.put((send_message,[channel,[0xdc,0x01,0x00,0x00,0x00,0x4d,0x00,0x00]],{}))
            #transmit_queue.put((send_message, [channel, [0xdc, 0x01, 0x00, 0x00, 0x14, 0x4d, 0x00, 0x00]], {}))
        
            #TODO: insert keep alive here

            thread.start_new_thread(slave_transmit, ())
                      
               

        self.daemon.requestLoop()

