#!/usr/bin/env python3

import time
import binascii

# Micropython doesn't have .zfill(w) function
# this replacement from their forums:
def zfill(s, width):
  # Pads the provided string with leading 0's to suit the specified 'chrs' length
  # Force # characters, fill with leading 0's
  return '{:0>{w}}'.format(s, w=width)

def tf(flag):
  if flag: return 'T'
  else: return 'F'

class Hex_value:
  # size is nibbles, not bytes
  @classmethod
  def check_hex(cls,text):
    # hexdigits = string.hexdigits: 
    # Micropython doesn't have string module
    hexdigits = '0123456789abcdefABCDEF'
    for ch in text:
      if ch not in hexdigits: 
        return False
    return True
  def __init__(self, value=0, size=4, vmin=None, vmax=None):
    self.ival = None
    self.size = size
    if vmin is None:
      self.vmin = 0
    else:
      self.vmin = vmin
    if vmax is None:
      self.vmax = pow(2,self.size*4)
    else:
      self.vmax = vmax
    if isinstance(value, str):
      self.from_string(value)
    elif isinstance(value, int):
      self.from_int(value)
    if self.ival is None:
      self.default()
  def default(self):
    self.ival = 0
    self.hval = zfill('0', self.size)
  def limits(self, value):
    if self.vmin is not None \
       and self.vmax is not None:
      return value >= self.vmin and value < self.vmax
    return True
  def from_int(self, value):
    self.default()
    if self.limits(value):
      self.ival = value
      self.hval = zfill( hex(value)[2:], self.size )
    return self
  def from_string(self, text):
    if self.check_hex(text) and len(text)<=self.size:
      self.ival = int(text,16)
      self.hval = zfill(text, self.size)
      if not self.limits(self.ival):
        self.default()
      return self
  def __eq__(a,b):
    return a.ival == b.ival
  def __gt__(a,b):
    return a.ival > b.ival
  def __str__(self):
    return '{:5d}\t0x{}'.format(self.ival, self.hval)
  def __repr__(self):
    return __str__()


class Parsing_status:
  def __init__(self, init=False):
    self.assign_all(init)
  def set_all(self):
    self.assign_all(True)
  def clr_all(self):
    self.assign_all(False)
  def assign_all(self, init):
    self.sync = init
    self.chret = init
    self.tabs = init
    self.size_packet = init
    self.size_size = init
    self.size_crc = init
    self.size_payload = init
    self.hex_size = init
    self.hex_crc = init
    self.crc = init
    self.valid = init
  def __bool__(self):
    return all( [
      self.sync, 
      self.chret, 
      self.tabs, 
      self.size_packet, 
      self.size_size, 
      self.size_crc, 
      self.size_payload, 
      self.hex_size, 
      self.hex_crc, 
      self.crc, 
      ] )
  def __str__(self):
    return '\nsync..............>  {}  sync pattern must be PACKET'.format( tf(self.sync) ) +\
      '\nchret.............>  {}  packet must end with CR'.format( tf(self.chret) ) +\
      '\ntabs..............>  {}  must be three tab separators'.format( tf(self.tabs) ) +\
      '\nsize of packet....>  {}  must be 22 bytes or larger'.format( tf(self.size_packet) ) +\
      '\nsize of size......>  {}  must be four bytes'.format( tf(self.size_size) ) +\
      '\nsize of crc.......>  {}  must be eight bytes'.format( tf(self.size_crc) ) +\
      '\nsize of payload...>  {}  must agree with size in packet'.format( tf(self.size_payload) ) +\
      '\nsize valid hex....>  {}  contains valid hexadecimal characters'.format( tf(self.hex_size) ) +\
      '\ncrc valid hex.....>  {}  contains valid hexadecimal characters'.format( tf(self.hex_crc) ) +\
      '\ncrc is valid......>  {}  crc calculations match crc in packet'.format( tf(self.crc) )
  def __repr__(self):
    return self.__str__()





class Packet:
  # Packet:
  # PACKET\t(LEN)\t(payload-goes-here)\t(crc)\n
  #   6   sync always 6 bytes
  #   4   len always 4 hex bytes
  #   x   payload variables length
  #   8   crc always 8 bytes
  #   4   tab characters 3 + cr 1 
  #  22 + x  Total Packet Size
  def __init__(self):
    self.overhead = 22
    self.sync = 'PACKET'
    self.size = Hex_value(0, size=4)
    self.payload = ''
    self.crc = Hex_value(0, size=8)
    self.stat = Parsing_status()
    self.reset()
  def reset(self):
    self.generate('')
  def __eq__(a,b):
    return a.payload == b.payload and a.size == b.size and a.crc == b.crc
  def __str__(self):
    return '{}\t{}\t{}\t{} ({})'.format(
        self.sync, self.size.hval, self.payload, self.crc.hval, tf(self.stat) )
  def __repr__(self):
    return self.__str__()
  def raw(self):
    return self.packet
  
  def generate(self, payload):
    self.payload = payload
    crc = binascii.crc32(bytes(self.payload,'latin_1'))
    print(crc)
    self.crc.from_int( crc )
    self.size.from_int( len(self.payload) )
    self.packet = '\t'.join([self.sync, self.size.hval, self.payload, self.crc.hval]) + '\r'
    self.stat.set_all()

  def parse(self, packet):
    self.valid = False
    pktsize = len(packet)
    self.stat.size_packet = pktsize >= self.overhead
    print('packet size:', pktsize)
    if self.stat.size_packet:
      self.stat.cr = packet.endswith('\r')
      print('ends with CR:', self.stat.cr)
      self.stat.sync = packet.startswith('PACKET')
      fields = packet.strip().split('\t')
      num_fields = len(fields)
      self.stat.tabs = num_fields == 4
      print('number of tabs:', num_fields)
      if self.stat.tabs:
        self.stat.size_size = fields[1] == 4
        self.stat.size_crc = fields[3] == 8
        self.stat.hex_size = Hex_value.check_hex(fields[1])
        self.stat.hex_crc = Hex_value.check_hex(fields[3])
        sync = fields[0]
        size = Hex_value(fields[1], size=4)
        payload = fields[2]
        crc = Hex_value(fields[3], size=8)
        print('sync:', sync)
        print('size:', size)
        print('payl:', payload)
        print(' crc:', crc)
        print('stat.size_size:', self.stat.size_size)
        print('stat.size_crc:', self.stat.size_crc)
        print('stat.hex_size:', self.stat.hex_size)
        print('stat.hex_crc:', self.stat.hex_crc)
        if all([ 
            self.stat.cr, self.stat.sync, 
            self.stat.size_size, self.stat.size_crc,
            self.stat.hex_size, self.stat.hex_crc 
        ] ):
          print('all okay')
          self.stat.size_payload = len(payload) == size.ival
          print('stat.size_payload:', self.stat.size_payload )
          if self.stat.size_payload:
            crc_calc = Hex_value( binascii.crc32(bytes(payload,'latin_1')), size=8 )
            self.stat.crc = crc == crc_calc
            print('stat.crc:', self.stat.crc )
            if self.stat.crc:
              print('finally!!!!')
              print('sync:', sync)
              print('size:', size)
              print('payload:', payload)
              print('crc:', crc)
              self.sync = sync
              self.size = size
              self.payload = payload
              self.crc = crc

    if not self.stat:
      self.reset()

  def untab(self, text):
    return text.replace('\t','{TAB}').replace('\r','{CR}')

  def retab(self, text):
    return text.replace( '{TAB}', '\t' ).replace('{CR}', '\r' )


def testme(message='hello'):

  print('====Generated packet p:')
  p = Packet()
  p.generate(message)
  print('message:', message)
  print('Packet:')
  print(p)


  print('====Parsed packet p2:')
  toparse = p.raw()
  p2 = Packet()
  p2.parse(toparse)
  print('toparse:', toparse)
  print('Packet:')
  print(p2)


  print('====Reply un-tabbed payload packet pr:')
  pr = Packet()
  utmessage = pr.untab(toparse)
  pr.generate(utmessage)
  print('untabbed:', utmessage)
  print('Packet:')
  print(pr)

  print('====Extract from received packet pck:')
  reply = pr.raw()
  pck = Packet()
  pck.parse(reply)
  print('reply:', reply)
  print('Packet:')
  print(pck)
  print('Extract payload:')
  kmsg = pck.retab(pck.payload)
  print(kmsg)

  return p, p2, pr, pck


#if __name__ == "__main__":
#  main()
