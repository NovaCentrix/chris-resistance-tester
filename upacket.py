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

class Bool_confirmed:
  UNK = 0
  TRUE = 1
  FALSE = 2
  ERROR = 3
  BSTRING = [ 'x', 'T', 'F', 'e' ]
  MIN = 0
  MAX = 3
  def from_bool(self, value):
    if value: self.flag = self.TRUE
    else:     self.flag = self.FALSE
  def from_string(self, value):
    if len(value)==0:
      self.flag = self.UNK
    #else:
    #  if value[0].lower in (b.lower() for b in self.BSTRING):
    #    self.flag=self.BSTRING.index(value[0])
    #  else:
    #    self.flag = self.UNK
    else:
      if value[0].lower() in (b.lower() for b in self.BSTRING):
        self.flag = next( i for i,v in enumerate(self.BSTRING) \
                              if v.lower() == value[0].lower() )
      else:
        self.flag = self.ERROR
  def to_string(self):
    return __str__(self)
  def __init__(self, flag=None):
    if flag is None: self.flag = self.UNK
    elif flag > self.MAX: self.flag = self.ERROR
    elif flag < self.MIN: self.flag = self.ERROR
    else: self.flag = flag
  def __bool__(self):
    return self.flag == self.TRUE
  def __eq__(a,b):
    if a.valid() and b.valid():
      return a.flag == b.flag
    else:
      return False
  def valid(self):
    return self.flag == self.TRUE or self.flag == self.FALSE
  def __str__(self):
    return self.BSTRING[ self.flag ]
  def __repr__(self):
    return self.__str__()

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
  def __init__(self):
    self.init_bools()
    self.set_lengths()
  def init_bools(self):
    # initialized all to unknown
    self.sync = Bool_confirmed()
    self.chret = Bool_confirmed()
    self.tabs = Bool_confirmed()
    self.size_packet = Bool_confirmed()
    self.size_size = Bool_confirmed()
    self.size_crc = Bool_confirmed()
    self.size_payload = Bool_confirmed()
    self.hex_size = Bool_confirmed()
    self.hex_crc = Bool_confirmed()
    self.crc = Bool_confirmed()
    self.valid = Bool_confirmed()
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
      '\nsync..............>  {}  sync pattern must be PACKET'.format( self.sync ) +\
      '\nchret.............>  {}  packet must end with CR'.format( self.chret ) +\
      '\ntabs..............>  {}  must be three tab separators'.format( self.tabs ) +\
      '\nsize of packet....>  {}  must be 22 bytes or larger'.format( self.size_packet ) +\
      '\nsize of size......>  {}  must be four bytes'.format( self.size_size ) +\
      '\nsize of crc.......>  {}  must be eight bytes'.format( self.size_crc ) +\
      '\nsize of payload...>  {}  must agree with size in packet'.format( self.size_payload ) +\
      '\nsize valid hex....>  {}  contains valid hexadecimal characters'.format( self.hex_size ) +\
      '\ncrc valid hex.....>  {}  contains valid hexadecimal characters'.format( self.hex_crc ) +\
      '\ncrc is valid......>  {}  crc calculations match crc in packet'.format( self.crc )
  def __repr__(self):
    return self.__str__()
  def serialize(self):
    return \
      '{},{},{},{},{};'.format( \
          self.len_packet, self.len_sync, self.len_size,\
          self.len_payload, self.len_crc ) + \
      '{},{},{},{},{},{},{},{},{},{}'.format( 
          self.sync, self.chret, self.tabs,
          self.size_packet, self.size_size, self.size_crc,
          self.size_payload, self.hex_size, self.hex_crc,
          self.crc )
  def unserialize(self, text):
    parts = text.strip().split(';')
    if len(parts) != 2: 
      self.init_bools()
      self.set_lengths()
      return False
    nums = parts[0].split(',')
    if len(nums) != 5:
      self.init_bools()
      self.set_lengths()
      return False
    flags = parts[1].split(',')
    if len(flags) != 10: 
      self.init_bools()
      self.set_lengths()
      return False
    self.len_packet   = nums[0]
    self.len_sync     = nums[1]
    self.len_size     = nums[2]
    self.len_payload  = nums[3]
    self.len_crc      = nums[4]
    self.sync.from_string(         flags[0] )
    self.chret.from_string(        flags[1] )
    self.tabs.from_string(         flags[2] )
    self.size_packet.from_string(  flags[3] )
    self.size_size.from_string(    flags[4] )
    self.size_crc.from_string(     flags[5] )
    self.size_payload.from_string( flags[6] )
    self.hex_size.from_string(     flags[7] )
    self.hex_crc.from_string(      flags[8] )
    self.crc.from_string(          flags[9] )
    return True

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
    pktsize = len(packet)
    status.len_packet = pktsize
    status.size_packet.from_bool( pktsize >= self.OVERHEAD )
    if self.vb: print('packet size:', pktsize)
    if status.size_packet:
      status.chret.from_bool( packet.endswith('\r') )
      if self.vb: print('ends with CR:', status.chret)
      fields = packet.strip().split('\t')
      num_fields = len(fields)
      status.tabs.from_bool( num_fields == 4 )
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
        status.size_size.from_bool( len(fields[1]) == 4 )
        status.size_crc.from_bool( len(fields[3]) == 8 )
        status.hex_size.from_bool( Hex_value.check_hex(fields[1]) )
        status.hex_crc.from_bool( Hex_value.check_hex(fields[3]) )
        sync = Packet_type( fields[0] )
        status.sync.from_bool( not sync.unknown )
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
          status.size_payload.from_bool( len(payload) == size.ival )
          if self.vb: print('stat.size_payload:', status.size_payload )
          if status.size_payload:
            crc_calc = Hex_value( binascii.crc32(bytes(payload,'latin_1')), size=8 )
            if self.vb: print('crc_calc:', crc_calc)
            status.crc.from_bool( crc == crc_calc )
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
