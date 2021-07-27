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

def check_hex(text):
  bytes_hexdigits = bytes(string.hexdigits,'latin_1')
  for ch in text:
    if ch not in string.hexdigits: 
      return False
  return True

class Parse_errors:
  def __init__(self):
    self.sync = False
    self.chret = False
    self.tabs = False
    self.size_packet = False
    self.size_size = False
    self.size_crc = False
    self.size_payload = False
    self.hex_size = False
    self.hex_src = False
    self.crc = False
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
      self.hex_src, 
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
      f'\ncrc valid hex.....>  {tf(self.hex_src)}   contains valid hexadecimal characters'  \
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
    self.reset()
  def reset(self):
    self.sync = 'PACKET'
    self.overhead = 22
    self.size = 0
    self.payload = ''
    self.crc=''
    self.valid = False
  def __eq__(a,b):
    return a.payload == b.payload and a.size == b.size and a.crc == b.crc
  def __str__(self):
    return f'{tf(self.valid)}:{self.sync}_{self.size}_{self.payload}_{self.crc}'
  def __repr__(self):
    return f'{tf(self.valid)}:{self.sync}_{self.size}_{self.payload}_{self.crc}'
  def raw(self):
    return self.packet
  def generate(self, payload):
    self.payload = payload
    self.crc = hex(binascii.crc32(bytes(self.payload,'latin_1')))[2:].zfill(8)
    self.size = hex(len(self.payload))[2:].zfill(4)
    self.packet = '\t'.join([self.sync, self.size, self.payload, self.crc]) + '\r'
    self.valid = True

  def parse(self, packet):
    pktsize = len(packet)
    self.ck_size_packet = pktsize >= 22
    print('packet size:', pktsize)
    if self.ck_size_packet:
      self.ck_cr = packet.endswith('\r')
      print('ends with CR:', self.ck_cr)
      self.ck_sync = packet.startswith('PACKET')
      fields = packet.strip().split('\t')
      num_fields = len(fields)
      self.ck_tabs = num_fields == 4
      print('number of tabs:', num_fields)
      if self.ck_tabs:
        sync = fields[0]
        size = fields[1]
        payload = fields[2]
        crc = fields[3]
        print('sync:', sync)
        print('size:', size)
        print('payl:', payload)
        print(' crc:', crc)
        self.ck_size_size = len(size) == 4
        self.ck_size_crc = len(crc) == 8
        self.ck_hex_size = check_hex(size)
        self.ck_hex_src = check_hex(crc)
        if all([ 
            self.ck_cr, self.ck_sync, 
            self.ck_size_size, self.ck_size_crc,
            self.ck_hex_size, self.ck_hex_crc 
        ] ):
          self.ck_size_payload = len(payload) == int(size,16)
          if self.ck_size_payload:
            crc_calc = hex(binascii.crc32(bytes(payload,'latin_1')))[2:].zfill(8)
            self.ck_crc = crc == crc_calc
            if self.ck_crc:
              # finally!!!!
              self.sync = sync
              self.crc = crc
              self.payload = payload
              self.size = size
              self.valid = True
          else:
            self.reset()
        # minimum packet size is size of CRC
        self.reset()



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

#if __name__ == "__main__":
#  main()
