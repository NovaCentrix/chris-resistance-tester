#!/usr/bin/env python3

import sys, signal
import serial
import time
import binascii
import string
import datetime as dt

def tf(flag):
  if flag: return 'T'
  else: return 'F'

class Hex_value:
  # size is nibbles, not bytes
  @classmethod
  def check_hex(cls,text):
    #bytes_hexdigits = bytes(string.hexdigits,'latin_1')
    for ch in text:
      if ch not in string.hexdigits: 
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
    self.hval = '0'.zfill(self.size)
  def limits(self, value):
    if self.vmin is not None \
       and self.vmax is not None:
      return value >= self.vmin and value < self.vmax
    return True
  def from_int(self, value):
    self.default()
    if self.limits(value):
      self.ival = value
      self.hval = hex(value)[2:].zfill(self.size)
    return self
  def from_string(self, text):
    if self.check_hex(text) and len(text)<=self.size:
      self.ival = int(text,16)
      self.hval = text.zfill(self.size)
      if not self.limits(self.ival):
        self.default()
      return self
  def __eq__(a,b):
    return a.ival == b.ival
  def __gt__(a,b):
    return a.ival > b.ival
  def __str__(self):
    return f'{self.ival:5d}\t0x{self.hval}'
  def __repr__(self):
    return f'{self.ival:5d}\t0x{self.hval}'


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
    return \
      f'\nsync..............>  {tf(self.sync)}   sync pattern must be PACKET' \
      f'\nchret.............>  {tf(self.chret)}   packet must end with CR'  \
      f'\ntabs..............>  {tf(self.tabs)}   must be three tab separators' \
      f'\nsize of packet....>  {tf(self.size_packet)}   must be 22 bytes or larger'  \
      f'\nsize of size......>  {tf(self.size_size)}   must be four bytes' \
      f'\nsize of crc.......>  {tf(self.size_crc)}   must be eight bytes'  \
      f'\nsize of payload...>  {tf(self.size_payload)}   must agree with size in packet'  \
      f'\nsize valid hex....>  {tf(self.hex_size)}   contains valid hexadecimal characters'  \
      f'\ncrc valid hex.....>  {tf(self.hex_crc)}   contains valid hexadecimal characters'  \
      f'\ncrc is valid......>  {tf(self.crc)}   crc calculations match crc in packet' 
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
    return f'{self.sync}\t{(self.size.hval)}\t{self.payload}\t{(self.crc.hval)} ({tf(self.stat)})'
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
        sync = fields[0]
        size = fields[1]
        payload = fields[2]
        crc = fields[3]
        print('sync:', sync)
        print('size:', size)
        print('payl:', payload)
        print(' crc:', crc)
        self.stat.size_size = len(size) == 4
        self.stat.size_crc = len(crc) == 8
        self.stat.hex_size = Hex_value.check_hex(size)
        self.stat.hex_crc = Hex_value.check_hex(crc)
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
          self.stat.size_payload = len(payload) == int(size,16)
          print('stat.size_payload:', self.stat.size_payload )
          if self.stat.size_payload:
            crc_calc = hex(binascii.crc32(bytes(payload,'latin_1')))[2:].zfill(8)
            self.stat.crc = crc == crc_calc
            print('stat.crc:', self.stat.crc )
            if self.stat.crc:
              print('finally!!!!')
              print('sync:', sync)
              print('size:', size)
              print('payload:', payload)
              print('crc:', crc)
              self.sync = sync
              self.size.from_string(size)
              self.payload = payload
              self.crc.from_string(crc)

    if not self.stat:
      self.reset()

  def untab(self, text):
    return text.replace('\t','{TAB}').replace('\r','{CR}')

  def retab(self, text):
    return text.replace( '{TAB}', '\t' ).replace('{CR}', '\r' )

class Corpus:
  def __init__( self, fname='source.agc' ):
    self.source = []
    self.fname = fname
    fp = open( self.fname, 'r' )
    if fp is None:
      print('Error opening file:', e)
      return
    # count the lines,
    # find maximum length
    self.maxlen = 0
    self.nlines = 0
    self.nbytes = 0
    self.n8bits = 0
    for line in fp:
      self.source.append( line.rstrip() )
      lenline = len(line)
      self.nbytes += lenline
      self.nlines += 1
      if lenline > self.maxlen: self.maxlen = lenline
      ##  for ch in line:
      ##    val = ch.encode('latin_1')
      ##    val = int.from_bytes( val, 'little' )
      ##    if val & 0x80: self.n8bits += 1
    print('nbytes:', self.nbytes)
    print('nlines:', self.nlines)
    print('maxlen:', self.maxlen)
    print('ttsend:', ttsend(self.nbytes, 115200))
    print('n8bits:', self.n8bits)
    fp.close()

def main():
  c = Corpus()
  p = Port()
  p = Packet()

  while True:
    for i,line in enumerate(c.source):
      time.sleep(0.005)
      px.generate(line)

p = Packet()
p.generate('hello')

msg = p.raw()
print(msg)

p2 = Packet()
p2.parse(msg)

pr = Packet()
rmsg = pr.untab(msg)
pr.generate(rmsg)
reply = pr.raw()

pck = Packet()
pck.parse(reply)
kmsg = pck.retab(pck.payload)


#if __name__ == "__main__":
#  main()
