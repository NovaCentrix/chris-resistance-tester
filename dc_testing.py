#!/usr/bin/env python

import sys, glob
from operator import itemgetter
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import datetime as dt
import csv


class DC_performance_tests:
  def __init__(self):
    meas = [ 
      [  0,     62.2,  3.294 ],
      [  6,     58.8,  2.949 ],
      [  10,    58.3,  2.755 ],
      [  15,    58.3,  2.493 ],
      [  16,    58.2,  2.42  ],
      [  16.5,  58.2,  2.42  ],
      [  17,    58.2,  2.38  ],
      [  17.5,  58.2,  2.36  ],
      [  18,    58.0,  2.34  ],
      [  18.5,  58.0,  2.32  ]
    ]
    self.tracer_ohms = [ m[0] for m in meas ]
    self.current = [ m[1] for m in meas ]
    self.voltage = [ m[2] for m in meas ]

  def plot_degridation( self, ax ):
    # Cumul error bytes, error ppm
    x = self.tracer_ohms
    y1 = self.current
    y2 = self.voltage

    print(x)
    print(y1)
    print(y2)

    ax.set_title(f'MCU Death by Resistance')

    major_ticks_x = np.arange(0,21,5)
    minor_ticks_x = np.arange(0,21,1)
    major_ticks_y = np.arange(55,65.1,1)
    minor_ticks_y = np.arange(55,65.1,0.25)
    icolor = 'crimson'
    vcolor = 'blue'

    ax.set_xlim(0,20)
    ax.set_ylim(55,65)
    ax.plot(x,y1, '-o', c=icolor )
    ax.set_xticks(major_ticks_x)
    ax.set_xticks(minor_ticks_x, minor=True)
    ax.set_yticks(major_ticks_y)
    ax.set_yticks(minor_ticks_y, minor=True)
    ax.tick_params(axis='y', labelcolor=icolor)
    ax.grid(which='both')
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)
    ax.set_xlabel('TraceR Resistance, Ohms')
    ax.set_ylabel('Current, mA', c=icolor )

    ax2 = ax.twinx()
    major_ticks_y2 = np.arange(2.3,3.31,0.1)
    ax2.tick_params(axis='y', labelcolor= vcolor )
    ax2.set_yticks(major_ticks_y2)
    ax2.set_ylim( 2.3, 3.3 )
    ax2.set_ylabel('MCU Voltage, volts', c=vcolor )
    ax2.plot(x, y2, '-o', c=vcolor )

    x3 = [ x[-1], x[-1] ]
    y3 = [ 0.0, 59 ]
    ax.plot( x3, y3, c='black', linewidth=2.0 )

    ax.annotate('Died @ 18.5 Ohms ', xy=(18.5, 59), xytext=(10, 63), 
       arrowprops=dict(color='black', 
         width=1.0,
         headwidth=5,
         shrink=0.00,
       ),
       horizontalalignment='center',
       verticalalignment='bottom',
     )

def main():
  dc = DC_performance_tests()

  nprows=1
  npcols=1
  vsize = 6
  hsize = 10
  fig, ax = plt.subplots(nrows=nprows, ncols=npcols, figsize=(hsize,vsize))
  title = 'DC Performance Testing'
  fig.canvas.manager.set_window_title('dc-performance-test')
  fig.suptitle(title, fontsize=20, fontweight='bold')

  dc.plot_degridation( ax )

  #fig.tight_layout(pad=1, w_pad = 1, h_pad = 1)
  plt.show()
  fig.savefig('dc_performance_plot.pdf')
  fig.savefig('dc_performance_plot.png')

if __name__ == "__main__":
  main()



