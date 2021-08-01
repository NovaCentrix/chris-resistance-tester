#!/usr/bin/env python3

import sys, signal
import serial
import time
import binascii
import string
import datetime as dt
import upacket

def ttsend( size, baud ):
  tbit = 1.0 / baud
  tbyte = 10.0 * tbit
  return size * tbyte

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


class Port:
  def __init__(self, portname='/dev/serial0', baud=115200):
    self.portname = portname
    self.baud = baud
    self.timeout = 0.5
    self.port = serial.Serial(
          self.portname, 
          baudrate = self.baud,
          timeout = self.timeout
        )
    print(self.port.name)
    self.port.reset_input_buffer()
    self.port.reset_output_buffer()

  def send( self, message ):
    return self.port.write( bytes(message, 'latin_1') )

  def recv( self, size ):
    buff = self.port.read( size )
    return buff.decode('latin_1')

class Logger:
  def __init__(self, fname):
    self.ready = False
    self.fp = open(fname, 'w')
    if self.fp is None: return
    self.ready = True
  def __bool__(self):
    return self.ready
  def separator_major(self):
    print('========================================================================', file=self.fp)
  def separator_minor(self):
    print('----------------------------------------', file=self.fp)
  def run_beg(self, descr):
    if not self.ready: return
    self.separator_major()
    print(descr, file=self.fp)
    self.t0 = dt.datetime.now()
    print('runbeg:', self.t0, file=self.fp)
    self.separator_minor()
  def run_end(self):
    if not self.ready: return
    self.t1 = dt.datetime.now()
    runtime = str(self.t1-self.t0)
    self.separator_minor()
    print('runend:', self.t1, file=self.fp)
    print('runtime:', runtime, file=self.fp)
  def close(self):
    if not self.ready: return
    self.fp.close()

class Counter:
  def __init__(self):
    self.reset()
  def reset(self):
    self.pkts=0
    self.bytes=0
  def accum(self, pkts, _bytes):
    self.pkts += pkts
    self.bytes += _bytes

class Tally:
  def __init__(self):
    self.all = Counter()
    self.err = Counter()
  def reset(self):
    self.all.reset()
    self.err.reset()

class Totals:
  def __init__(self):
    self.prg = Tally()
    self.run = Tally()
  def all_accum(self, pkts, _bytes):
    self.prg.all.accum( pkts, _bytes)
    self.run.all.accum( pkts, _bytes)
  def err_accum(self, pkts, _bytes):
    self.prg.err.accum( pkts, _bytes)
    self.run.err.accum( pkts, _bytes)
  def run_reset(self):
    self.run.all.reset()
    self.run.err.reset()

def main():

  c = Corpus()
  p = Port()
  px = upacket.Packet()
  pr = upacket.Packet()
  retry = 10

  totals = Totals() # tally of data and errors

  logger = Logger('logfile.txt')
  if not logger:
    print('error opening logfile')
    exit(99)

  for run in range(4):
    logger.run_beg(f'Run # {run}')
    totals.run.reset()

    for i,line in enumerate(c.source):
      time.sleep(0.005)
      px.generate(line)
      nsent = p.send(px.packet)
      totals.all_accum( 1, int(px.size) )
      #buff = p.recv(nsent)
      buff = p.recv(1024)
      stat = pr.parse(buff)
      obuff = upacket.Packet.unserialize(pr.payload)
      stats = po.parse(obuff)
      #print(stats)
      match = px == po
      if not match:
        totals.err_accum( 1, int(px.size) )
        print(px.size, nsent, len(buff), pr==px, file=logger.fp)
        print('  px:', px, file=logger.fp)
        print('  pr:', pr, file=logger.fp)
        print('  po:', po, file=logger.fp)
      if i % 1000 == 0:
        print(f'Run {run}: '
              f'{totals.run.all.pkts:12} {totals.run.all.bytes:12}   '
              f'{totals.run.err.pkts:12} {totals.run.err.bytes:12}')
    print(f'Run {run} Completed')
    prg_error = float(totals.prg.err.bytes) / float(totals.prg.all.bytes)
    prg_error100 = prg_error * 100.0
    prg_error1e6 = prg_error * 1.0e6
    run_error = float(totals.run.err.bytes) / float(totals.run.all.bytes)
    run_error100 = run_error * 100.0
    run_error1e6 = run_error * 1.0e6
    logger.separator_minor()
    print(f'Total packets...> {totals.run.all.pkts:12} \t{totals.prg.all.pkts:12}',  file=logger.fp )
    print(f'Total bytes.....> {totals.run.all.bytes:12}\t{totals.prg.all.bytes:12}', file=logger.fp )
    print(f'Error packets...> {totals.run.err.pkts:12} \t{totals.prg.err.pkts:12}',  file=logger.fp )
    print(f'Error bytes.....> {totals.run.err.bytes:12}\t{totals.prg.err.bytes:12}', file=logger.fp )
    print(f'Error percent...> {run_error100:12.2f} %\t{prg_error100:12.2f} %', file=logger.fp )
    print(f'Error ppm.......> {run_error1e6:12.2f} ppm\t{prg_error1e6:12.2f} ppm', file=logger.fp )
    logger.run_end()

  logger.close()


def main2(npackets=None, vb=False):
  """Main2: for manual ops, xmts, summary on screen, no logging"""

  c = Corpus()
  p = Port()
  px = upacket.Packet() # original packet to send
  pr = upacket.Packet() # echoed back from tarte-py
  po = upacket.Packet() # reconstructed original packet
  pa = upacket.Packet() # ack/nak packet
  retry = 10
  asc = upacket.Ascii()

  totals = Totals() # tally of data and errors

  looping = True
  while looping:
    for i,line in enumerate(c.source):
      time.sleep(0.030)
      if npackets is not None:
        if i >= npackets:
          looping=False
          break
      px.generate(line)
      nsent = p.send(px.packet)
      totals.all_accum( 1, int(px.size) )
      #buff = p.recv(nsent)
      # Get the reply
      buff = p.recv(2048)
      packets = buff.split(px.RSEP)
      if len(packets) != 2:
        print('\nNumber received packets not two')
        print('  Sent:')
        print('  ', px)
        print('  Received buff:')
        print('  ', asc.pretty(buff))
        print('  len packets', len(packets))
        print('  packets:')
        for ppp in packets: 
          print(ppp)
        exit()
      rbuff = packets[0]
      abuff = packets[1]
      stat = pr.parse(rbuff)
      obuff = upacket.Packet.unserialize(pr.payload)
      stats = po.parse(obuff)
      #print(stats)
      pa.parse(abuff)
      match = px == po
      if vb:
        print('-----')
        print('  px:', px)
        print('  pr:', pr)
        print('  po:', po)
        print('  pa:', pa)

      if not match:
        totals.err_accum( 1, int(px.size) )
        print('\nReceived packet does not match')
        print(px.size, nsent, len(buff), pr==px)
        print('  Sent:')
        print('  ', px)
        print('  Received buff:')
        print('  ', asc.pretty(buff))
        print('  px:', px)
        print('  pr:', pr)
        print('  po:', po)
        print('  pa:', pa)
        exit()

      if i % 100 == 0:
        print( f'{totals.run.all.pkts:12} {totals.run.all.bytes:12}   '
               f'{totals.run.err.pkts:12} {totals.run.err.bytes:12}',
               end='\r')


#if __name__ == "__main__":
#  main()
