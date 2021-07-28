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

class Packet_type:
  # packet type will always contain valid string
  # flag self.unknown will be set, however, if an
  # invalid string was used to initialize the 
  # packet type
  TYPES = { 'packet': 'PACKET', 'acknak': 'ACKNAK' }
  def __init__(self, stype='packet'):
    self.set_ptype(stype)
  def __eq__(a,b):
    return a.ptype == b.ptype
  def __str__(self):
    return '{}'.format(self.ptype)
  def __repr__(self):
    return self.__str__()
  def validate(self, stype):
    return stype.lower() in self.TYPES
  def set_ptype(self, stype='packet'):
    if self.validate(stype):
      self.unknown = False
      self.ptype = self.TYPES[stype.lower()]
    else:
      self.unknown = True
      self.ptype = self.TYPES['packet']

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
    self.set_lengths()
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

  def set_lengths( self, lpacket=0, lsync=0, lsize=0, lpayload=0, lcrc=0 ):
    self.len_packet = lpacket
    self.len_sync = lsync
    self.len_size = lsize
    self.len_payload = lpayload
    self.len_crc = lcrc

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
    return \
      '\nlen of packet.....>  {}  bytes'.format( self.len_packet ) +\
      '\nlen of sync.......>  {}  bytes'.format( self.len_sync ) +\
      '\nlen of size.......>  {}  bytes'.format( self.len_size ) +\
      '\nlen of payload....>  {}  bytes'.format( self.len_payload ) +\
      '\nlen of crc........>  {}  bytes'.format( self.len_crc ) +\
      '\nsync..............>  {}  sync pattern must be PACKET'.format( tf(self.sync) ) +\
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
  OVERHEAD = 22
  def __init__(self, payload='', stype='packet'):
    self.vb=False # verbosity
    self.stat = Parsing_status()
    self.generate(payload, stype)
  def __eq__(a,b):
    return a.sync == b.sync and \
           a.payload == b.payload and \
           a.size == b.size and \
           a.crc == b.crc
  def __str__(self):
    #return '{}\t{}\t{}\t{} ({})'.format(
    return '{} / {} / {} / {}   ({})'.format(
        self.sync, self.size.hval, self.payload, self.crc.hval, tf(self.stat) )
  def __repr__(self):
    return self.__str__()
  def raw(self):
    return self.packet
  
  def build(self):
    self.packet = '\t'.join([str(self.sync), self.size.hval, self.payload, self.crc.hval]) + '\r'

  def reset(self):
    self.generate()

  def generate(self, payload='', stype='packet'):
    self.sync = Packet_type(stype)
    self.payload = payload
    self.size = Hex_value(len(self.payload), size=4)
    crc = binascii.crc32(bytes(self.payload,'latin_1'))
    self.crc = Hex_value( crc, size=8)
    self.build()
    self.stat.set_all()
    self.stat.set_lengths(len(self.packet), 6, 4, len(self.payload), 8)

  def parse(self, packet):
    self.stat.clr_all()
    self.valid = False
    pktsize = len(packet)
    self.stat.len_packet = pktsize
    self.stat.size_packet = pktsize >= self.OVERHEAD
    if self.vb: print('packet size:', pktsize)
    if self.stat.size_packet:
      self.stat.cr = packet.endswith('\r')
      if self.vb: print('ends with CR:', self.stat.cr)
      fields = packet.strip().split('\t')
      num_fields = len(fields)
      self.stat.tabs = num_fields == 4
      if self.vb: print('number of tabs:', num_fields)
      if self.stat.tabs:
        if self.vb: print('fields0.sync:', fields[0])
        if self.vb: print('fields1.size:', fields[1])
        if self.vb: print('fields2.payl:', fields[2])
        if self.vb: print('fields3.crc :', fields[3])
        self.stat.len_sync = len(fields[0])
        self.stat.len_size = len(fields[1])
        self.stat.len_payload = len(fields[2])
        self.stat.len_crc = len(fields[3])
        self.stat.size_size = len(fields[1]) == 4
        self.stat.size_crc = len(fields[3]) == 8
        self.stat.hex_size = Hex_value.check_hex(fields[1])
        self.stat.hex_crc = Hex_value.check_hex(fields[3])
        sync = Packet_type( fields[0] )
        self.stat.sync = not sync.unknown
        size = Hex_value(fields[1], size=4)
        payload = fields[2]
        crc = Hex_value(fields[3], size=8)
        if self.vb: print('sync:', sync)
        if self.vb: print('size:', size)
        if self.vb: print('payl:', payload)
        if self.vb: print(' crc:', crc)
        if self.vb: print('stat.size_size:', self.stat.size_size)
        if self.vb: print('stat.size_crc:', self.stat.size_crc)
        if self.vb: print('stat.hex_size:', self.stat.hex_size)
        if self.vb: print('stat.hex_crc:', self.stat.hex_crc)
        if all([ 
            self.stat.cr, self.stat.sync, 
            self.stat.size_size, self.stat.size_crc,
            self.stat.hex_size, self.stat.hex_crc 
        ] ):
          if self.vb: print('all okay')
          self.stat.size_payload = len(payload) == size.ival
          if self.vb: print('stat.size_payload:', self.stat.size_payload )
          if self.stat.size_payload:
            crc_calc = Hex_value( binascii.crc32(bytes(payload,'latin_1')), size=8 )
            if self.vb: print('crc_calc:', crc_calc)
            self.stat.crc = crc == crc_calc
            if self.vb: print('stat.crc:', self.stat.crc )
            if self.stat.crc:
              if self.vb: print('finally!!!!')
              if self.vb: print('sync:', sync)
              if self.vb: print('size:', size)
              if self.vb: print('payload:', payload)
              if self.vb: print('crc:', crc)
              self.sync = sync
              self.size = size
              self.payload = payload
              self.crc = crc
              self.build()

    if not self.stat:
      self.reset()

  @classmethod
  def untab(cls, text):
    return text.replace('\t','{TAB}').replace('\r','{CR}')

  @classmethod
  def retab(cls, text):
    return text.replace( '{TAB}', '\t' ).replace('{CR}', '\r' )


def testme(message='hello'):

  print('====Generated packet p:')
  p = Packet()
  p.generate(message)
  print('message:', message)
  print('P Packet:')
  print(p)


  print('====Parsed packet p2:')
  toparse = p.raw()
  p2 = Packet()
  p2.parse(toparse)
  print('toparse:', toparse)
  print('P2 Packet:')
  print(p2)


  print('====Reply un-tabbed payload packet pr:')
  pr = Packet()
  untab_msg = pr.untab(toparse)
  pr.generate(untab_msg)
  print('untabbed:', untab_msg)
  print('PR Packet:')
  print(pr)

  print('====Extract from received packet pck:')
  reply = pr.raw()
  pck = Packet()
  pck.parse(reply)
  print('reply:', reply)
  print('Packet:')
  print(pck)

  print('====Extracted packet again from payload:')
  kmsg = pck.payload
  print('Extracted payload:', kmsg)
  p0 = Packet()
  retab_msg = p0.retab(kmsg)
  print('Retabbed payload:', retab_msg)
  p0.parse(retab_msg)
  print('P0 Original Packet:')
  print(p0)



#if __name__ == "__main__":
#  main()
