#!/usr/bin/env python

import sys, glob
from operator import itemgetter
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import csv


class Results:
  def __init__( self, fname, run ):
    self.fname = fname
    self.run = run
    self.tot_pkts = 0
    self.tot_bytes = 0
    self.err_pkts = 0
    self.err_bytes = 0
    self.error100 = 0.0
    self.error1e6 = 0.0
    self.runtime = ''
  def set_totals( tot_pkts, tot_bytes ):
    self.tot_pkts = tot_pkts
    self.tot_bytes = tot_bytes
  def set_errors( err_pkts, err_bytes, err100, err1e6 ):
    self.err_pkts = err_pkts
    self.err_bytes = err_bytes
    self.err100 = err100
    self.err1e6 = err1e6
  def __str__(self):
    return f'\n'\
           f'File: {self.fname}, Run: {self.run}\n'\
           f'Total packets...> {self.tot_pkts:12}\n'\
           f'Total bytes.....> {self.tot_bytes:12}\n'\
           f'Error packets...> {self.err_pkts:12}\n'\
           f'Error bytes.....> {self.err_bytes:12}\n'\
           f'Error percent...> {self.error100:12.2f} %\n'\
           f'Error ppm.......> {self.error1e6:12.2f} ppm\n'\
           f'Runtime.........> {self.runtime}'
  def __repr__(self):
    return f'Run: {self.fname}:{self.run}'
    # Format of log file summaries to grab, 
    # four runs per file:
    # Total packets...>        65614 	       65614
    # Total bytes.....>      2217118	     2217118
    # Error packets...>           31 	          31
    # Error bytes.....>         1258	        1258
    # Error percent...>         0.06 %	        0.06 %
    # Error ppm.......>       567.40 ppm	      567.40 ppm
    # ----------------------------------------
    # runend: 2021-07-21 16:18:38.020497
    # runtime: 0:15:31.791822

class Logfile:
  def __init__(self):
    self.runs = []
  def load(self, fname, ohms):
    self.fname = fname
    self.ohms = ohms
    with open(fname, 'r') as fin:
      self.cumul = Results( fname, 'cumulative' )
      for line in fin:
        fields = line.split()
        if fields[0] == 'Run' and fields[1] == '#':
          runnum = fields[2]
          results = Results( fname, runnum )
          print('run:', fname, runnum)
        if fields[0] == 'Total':
          if fields[1] == 'packets...>':
            results.tot_pkts = int(fields[2])
            self.cumul.tot_pkts = int(fields[3])
          if fields[1] == 'bytes.....>':
            results.tot_bytes = int(fields[2])
            self.cumul.tot_bytes = int(fields[3])
        if fields[0] == 'Error':
          if fields[1] == 'packets...>':
            results.err_pkts = int(fields[2])
            self.cumul.err_pkts = int(fields[3])
          if fields[1] == 'bytes.....>':
            results.err_bytes = int(fields[2])
            self.cumul.err_bytes = int(fields[3])
          if fields[1] == 'percent...>':
            results.error100 = float(fields[2])
            self.cumul.error100 = float(fields[4])
          if fields[1] == 'ppm.......>':
            results.error1e6 = float(fields[2])
            self.cumul.error1e6 = float(fields[4])
        if fields[0] == 'runtime:':
            results.runtime = fields[1]
            self.cumul.runtime = fields[1]
            self.runs.append(results)


class SerialTests:
  def __init__(self):
    self.logdir = './logs/'
    self.logfiles = [ 
        'log-shunt.txt', 'log-r011.txt', 'log-r075.txt', 
        'log-r150.txt', 'log-r225.txt', 'log-r270.txt' ]
    self.tracer_ohms = [ 0, 11, 75, 150, 225, 270 ]
    self.logs = []
    for i in range( len(self.logfiles) ):
      lf = self.logfiles[i]
      ohms = self.tracer_ohms[i]
      log = Logfile()
      log.load(self.logdir+lf, ohms)
      self.logs.append( log )


  def plot_errors( self, ax ):
    # Cumul error bytes, error ppm
    x = []
    y1 = []
    y2 = []
    for log in self.logs:
      print(log.ohms)
      x.append( log.ohms )
      y1.append( log.cumul.err_bytes )
      y2.append( log.cumul.error1e6 )

    print(x)
    print(y1)
    print(y2)

    ax.set_title(f'Total #bytes ~6.2 MB per Resistance Setting')

    major_ticks_x = np.arange(0,301,50)
    minor_ticks_x = np.arange(0,301,10)
    major_ticks_y = np.arange(0,601,100)
    minor_ticks_y = np.arange(0,601,25)

    ax.set_xlim(0,300)
    ax.set_ylim(0,600)
    ax.plot(x,y2, '-o', c='b' )
    ax.set_xticks(major_ticks_x)
    ax.set_xticks(minor_ticks_x, minor=True)
    ax.set_yticks(major_ticks_y)
    ax.set_yticks(minor_ticks_y, minor=True)
    ax.tick_params(axis='y', labelcolor='b')
    ax.grid(which='both')
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)
    ax.set_xlabel('TraceR Resistance, Ohms')
    ax.set_ylabel('Error, PPM', c='b')

def main():
  st = SerialTests()

  nprows=1
  npcols=1
  vsize = 6
  hsize = 10
  fig, ax = plt.subplots(nrows=nprows, ncols=npcols, figsize=(hsize,vsize))
  title = 'Serial Link Test Data'
  fig.canvas.manager.set_window_title('serial-link-test')
  fig.suptitle(title, fontsize=20, fontweight='bold')

  st.plot_errors( ax )

  #fig.tight_layout(pad=1, w_pad = 1, h_pad = 1)
  plt.show()
  fig.savefig('collate_plot.pdf')
  fig.savefig('collate_plot.png')

if __name__ == "__main__":
  main()

