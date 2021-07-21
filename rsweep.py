#!/usr/bin/env python3

from tracer import Tracer
import keithley
import time
import datetime as dt
import sys
import statistics as stats

import pyvisa as visa
import rigol1000z

def main(argv):

  if len(argv) < 2:
    print('Usage: rsweel <1,2>   for R1 or R2')
    exit(0)
  if argv[1] != '1' and argv[1] != '2':
    print('Error, must specify R1 or R2')
    print('Usage: check <1,2>   for R1 or R2')
    exit(0)

  if len(argv) > 2:
    init_comms = '1' == argv[2]
  else:
    init_comms = True

  print('=== Initializing Rigol DS1054Z Oscilloscope ===')
  myscope = 'TCPIP0::192.168.1.220::INSTR'
  rm = visa.ResourceManager()
  resource = rm.open_resource(myscope)
  scope = rigol1000z.Rigol1000z(resource)
  # this test assumes the scope is already setup
  # and configured for screenshots

  print('=== Initializing TraceR Module ===')
  Tracer.init_serial('/dev/ttyACM1')
  if init_comms:
    if not Tracer.init_comm_link():
      print('failed to initialize TraceR comm link')
      exit(0)
  tr1 = Tracer(Tracer.TR1)
  tr2 = Tracer(Tracer.TR2)

  if argv[1] == '1':
    tr = tr1 
  elif argv[1] == '2':
    tr = tr2 

  # get serial number and make filename
  tr.command(tr.IDENT)
  print('TraceR:', tr.ident.lower(), tr.which)
  
  print('=== Sweeping TraceR Resistance ===')
  for rcmd in range(0,300,25):

    tr.command(Tracer.OHMS, rcmd)
    print('# rcmd, ohms:', rcmd, tr.ohms)
    time.sleep(0.100)
    png_fname = f'rsweep-{rcmd:03}-ohms.png'
    png = scope.get_screenshot( png_fname, 'png' )
    with open(png_fname, 'wb') as fpng:
      fpng.write(png)


  print('Finished')

if __name__ == "__main__":
  main(sys.argv)

