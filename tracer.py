#!/usr/bin/env python3
import serial
from time import sleep
from datetime import datetime, timedelta

class Tracer:
  TR1 = '1'
  TR2 = '2'
  COUNTS = 'X'
  RELAYS = 'K'
  OHMS = 'R'
  ASSIGN = '='
  QUERY = '?'
  IDENT = 'I'
  END = '\n'
  ser = None
  port = None

  @classmethod
  def init_serial(cls,port):
    if cls.ser is None:
      cls.port = port
      cls.ser = serial.Serial( Tracer.port,
                     baudrate = 115200,
                     stopbits = serial.STOPBITS_ONE,
                     bytesize = serial.EIGHTBITS,
                     writeTimeout = 0,
                     timeout = 0.250,
                     rtscts = False,
                     dsrdtr = False )

  @classmethod
  def init_comm_link(cls):
    """Sends ctrl-C and ctrl-D to soft reboot"""
    cls.ser.reset_input_buffer()
    cls.ser.write(b'\x03')
    sleep(1.0)
    buff = str(cls.ser.read(1024).decode('ascii'))
    if buff.endswith('\r\n>>> '):
      print('TraceR Module, Ctrl-C successful')
    else:
      print('TraceR Module, Ctrl-C unsuccessful, buff:')
      print(buff)
      return False
    cls.ser.write(b'\x04')
    sleep(8.0)
    buff = str(cls.ser.read(1024).decode('ascii'))
    #if buff.endswith('soft reboot\r\n\r\n> '):
    if buff.endswith('Type "H" for help\r\n\r\n> '):
      print('TraceR Module, soft reboot successful')
    else:
      print('TraceR Module, soft reboot unsuccessful, buff:')
      print(buff)
      return False
    return True

  def __init__(self, which):
    self.which=which
    self.counts=0
    self.relay=0
    self.ohms=0
    self.ident=''

  def __repr__(self):
    return f'{self.which}: {self.counts}.{self.relay} = {self.ohms}'

  def parse_reply(self,reply):
    #print('parsing reply:', reply)
    lines = reply.split('\n')
    #print('lines:', lines)
    echo = lines[0].strip()
    status = lines[1].strip()
    fields = status.split(' ')
    for f in fields: 
      #print('f:', f)
      key,val = f.split('=')
      param=key[0]
      if len(key) > 1: which=key[1]
      #print('broken:', key, param, which, val)
      #print('which compare:', which, self.which)
      #print('param:', param)
      #print('value:', val)
      if param == Tracer.COUNTS:
        #print('param matched counts')
        self.counts = int(val)
      elif param == Tracer.RELAYS:
        #print('param matched relays')
        self.relay = val
      elif param == Tracer.OHMS:
        #print('param matched ohms')
        self.ohms = float(val)
      elif param == Tracer.IDENT:
        self.ident = val
      else:
        #print('param matched nothing')
        pass


  def command(self, param, value=None):
    if param == self.IDENT:
      cmd_string = param + self.END
    else:
      cmd_string = param + self.which
      if value is None:
        cmd_string += self.QUERY + self.END
      else:
        cmd_string += Tracer.ASSIGN + str(value) + self.END

    nwrite = self.ser.write( bytes(cmd_string.encode('ascii')) )
    #print('command:')
    #print(cmd_string.strip())
    #print('end-of-command:')
    reply = str(Tracer.ser.read(1024).decode('ascii'))[nwrite:]
    #print('reply:')
    #print(reply.strip())
    #print('end-of-reply:')
    self.parse_reply(reply)

def testme(init=False):
  Tracer.init_serial('/dev/ttyACM0')
  if init:
    if not Tracer.init_comm_link():
      print('failed to initialize comm link')
      exit(0)
  tr1 = Tracer(Tracer.TR1)
  tr2 = Tracer(Tracer.TR2)
  # tr.parse_reply('X1=0\r\nX1=0 K1=open\r\n> ')
  tr1.command(Tracer.COUNTS, 55)
  print(tr1.counts)
  return [tr1, tr2]

def set_both(init=False, portname = '/dev/ttyACM0' ):
  Tracer.init_serial(portname)
  if init:
    if not Tracer.init_comm_link():
      print('failed to initialize comm link')
      exit(0)
  tr1 = Tracer(Tracer.TR1)
  tr2 = Tracer(Tracer.TR2)
  while(True):
    print('ohms? ', end='')
    str_ohms = input()
    if str_ohms == 'quit': break
    if str_ohms == 'end': break
    if str_ohms == 'short':
      tr1.command(Tracer.RELAYS, 1)
      tr2.command(Tracer.RELAYS, 1)
      print('Relays:', tr1.relay, tr2.relay)
    elif str_ohms == 'open':
      tr1.command(Tracer.RELAYS, 0)
      tr2.command(Tracer.RELAYS, 0)
      print('Relays:', tr1.relay, tr2.relay)
    else:
      try:
        ohms = int(2*float(str_ohms)+0.5)
        tr1.command(Tracer.OHMS, ohms)
        tr2.command(Tracer.OHMS, ohms)
        parallel = 1.0 / (1.0/tr1.ohms + 1.0/tr2.ohms)
        print('Ohms:', tr1.ohms, tr2.ohms, 'Parallel:', parallel)
      except:
        print('invalid input:', str_ohms)

#portmac = '/dev/cu.usbmodem147101'
