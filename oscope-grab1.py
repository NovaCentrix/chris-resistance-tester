#!/usr/bin/env python3

import keithley
import time
import datetime as dt
import sys
import pyvisa as visa
import rigol1000z

def main(argv):

  print('=== Initializing Rigol DS1054Z Oscilloscope ===')
  myscope = 'TCPIP0::192.168.1.220::INSTR'
  rm = visa.ResourceManager()
  resource = rm.open_resource(myscope)
  scope = rigol1000z.Rigol1000z(resource)
  # this test assumes the scope is already setup
  # and configured for screenshots

  png_fname = 'rigol-screencap.png'
  png = scope.get_screenshot( png_fname, 'png' )
  with open(png_fname, 'wb') as fpng:
    fpng.write(png)

  print('Finished')

if __name__ == "__main__":
  main(sys.argv)

