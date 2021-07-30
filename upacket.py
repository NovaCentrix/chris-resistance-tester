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
  PTYPE_DEF = 'pksend'
  PTYPES = { 'pksend': 'PKSEND', 
             'pkecho': 'PKECHO', 
             'acknak': 'ACKNAK',
          }
  def __init__(self, stype=None):
    self.set_ptype(stype)
  def __eq__(a,b):
    return a.ptype == b.ptype
  def __str__(self):
    return '{}'.format(self.ptype)
  def __repr__(self):
    return self.__str__()
  def validate(self, stype):
    return stype.lower() in self.PTYPES
  def set_ptype(self, stype=None):
    if stype is None: stype = self.PTYPE_DEF
    if self.validate(stype):
      self.unknown = False
      self.ptype = self.PTYPES[stype.lower()]
    else:
      self.unknown = True
      self.ptype = self.PTYPES[self.PTYPE_DEF]

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
  def serialize(self):
    return \
      '{},{},{},{},{};'.format( \
          self.len_packet, self.len_sync, self.len_size,\
          self.len_payload, self.len_crc ) + \
      '{},{},{},{},{},{},{},{},{},{}'.format( 
          tf(self.sync), tf(self.chret), tf(self.tabs),
          tf(self.size_packet), tf(self.size_size), tf(self.size_crc),
          tf(self.size_payload), tf(self.hex_size), tf(self.hex_crc),
          tf(self.crc) )
  def unserialize(self, text):
    parts = text.strip().split(';')
    if len(parts) != 2: return False
    nums = parts[0].split(',')
    if len(nums) != 5: return False
    flags = parts[1].split(',')
    if len(flags) != 10: return False
    self.len_packet   = nums[0]
    self.len_sync     = nums[1]
    self.len_size     = nums[2]
    self.len_payload  = nums[3]
    self.len_crc      = nums[4]
    self.sync         = flags[0] == 'T'
    self.chret        = flags[1] == 'T'
    self.tabs         = flags[2] == 'T'
    self.size_packet  = flags[3] == 'T'
    self.size_size    = flags[4] == 'T'
    self.size_crc     = flags[5] == 'T'
    self.size_payload = flags[6] == 'T'
    self.hex_size     = flags[7] == 'T'
    self.hex_crc      = flags[8] == 'T'
    self.crc          = flags[9] == 'T'

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
  def __init__(self, payload='', stype=None):
    self.vb=False # verbosity
    self.generate(payload, stype)
  def __eq__(a,b):
    return a.sync == b.sync and \
           a.payload == b.payload and \
           a.size == b.size and \
           a.crc == b.crc
  def __str__(self):
    #return '{}\t{}\t{}\t{} ({})'.format(
    return '{} / {} / {} / {}'.format(
        self.sync, self.size.hval, self.payload, self.crc.hval )
  def __repr__(self):
    return self.__str__()
  def raw(self):
    return self.packet
  
  def build(self):
    self.packet = '\t'.join([str(self.sync), self.size.hval, self.payload, self.crc.hval]) + '\r'

  def reset(self):
    self.generate()

  def generate(self, payload='', stype=None):
    self.sync = Packet_type(stype)
    self.payload = payload
    self.size = Hex_value(len(self.payload), size=4)
    crc = binascii.crc32(bytes(self.payload,'latin_1'))
    self.crc = Hex_value( crc, size=8)
    self.build()

  def parse(self, packet):
    status = Parsing_status()
    status.clr_all()
    pktsize = len(packet)
    status.len_packet = pktsize
    status.size_packet = pktsize >= self.OVERHEAD
    if self.vb: print('packet size:', pktsize)
    if status.size_packet:
      status.chret = packet.endswith('\r')
      if self.vb: print('ends with CR:', status.chret)
      fields = packet.strip().split('\t')
      num_fields = len(fields)
      status.tabs = num_fields == 4
      if self.vb: print('number of tabs:', num_fields)
      if status.tabs:
        if self.vb: print('fields0.sync:', fields[0])
        if self.vb: print('fields1.size:', fields[1])
        if self.vb: print('fields2.payl:', fields[2])
        if self.vb: print('fields3.crc :', fields[3])
        status.len_sync = len(fields[0])
        status.len_size = len(fields[1])
        status.len_payload = len(fields[2])
        status.len_crc = len(fields[3])
        status.size_size = len(fields[1]) == 4
        status.size_crc = len(fields[3]) == 8
        status.hex_size = Hex_value.check_hex(fields[1])
        status.hex_crc = Hex_value.check_hex(fields[3])
        sync = Packet_type( fields[0] )
        status.sync = not sync.unknown
        size = Hex_value(fields[1], size=4)
        payload = fields[2]
        crc = Hex_value(fields[3], size=8)
        if self.vb: print('sync:', sync)
        if self.vb: print('size:', size)
        if self.vb: print('payl:', payload)
        if self.vb: print(' crc:', crc)
        if self.vb: print('stat.size_size:', status.size_size)
        if self.vb: print('stat.size_crc:', status.size_crc)
        if self.vb: print('stat.hex_size:', status.hex_size)
        if self.vb: print('stat.hex_crc:', status.hex_crc)
        if all([ 
            status.chret, status.sync, 
            status.size_size, status.size_crc,
            status.hex_size, status.hex_crc 
        ] ):
          if self.vb: print('all okay')
          status.size_payload = len(payload) == size.ival
          if self.vb: print('stat.size_payload:', status.size_payload )
          if status.size_payload:
            crc_calc = Hex_value( binascii.crc32(bytes(payload,'latin_1')), size=8 )
            if self.vb: print('crc_calc:', crc_calc)
            status.crc = crc == crc_calc
            if self.vb: print('stat.crc:', status.crc )
            if status.crc:
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
    if not status:
      self.reset()

    return status

  @classmethod
  def untab(cls, text):
    return text.replace('\t','{TAB}').replace('\r','{CR}')

  @classmethod
  def retab(cls, text):
    return text.replace( '{TAB}', '\t' ).replace('{CR}', '\r' )


#def testme(message='hello'):
message = 'hello'
if True:

  print('====Generated packet p:')
  p = Packet()
  p.generate(message)
  print('message:', message)
  print('P Packet:')
  print(p)


  print('====Parsed packet p2:')
  toparse = p.raw()
  p2 = Packet()
  p2_status = p2.parse(toparse)
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
  pck_status = pck.parse(reply)
  print('reply:', reply)
  print('Packet:')
  print(pck)

  print('====Extracted packet again from payload:')
  kmsg = pck.payload
  print('Extracted payload:', kmsg)
  p0 = Packet()
  retab_msg = p0.retab(kmsg)
  print('Retabbed payload:', retab_msg)
  p0_status = p0.parse(retab_msg)
  print('P0 Original Packet:')
  print(p0)




#if __name__ == "__main__":
#  main()
