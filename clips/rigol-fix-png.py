#!/usr/bin/env python3

# The MAIN code takes a bunch of images
# (typically oscope screen-shots, for example)
# and adds some text to the screen and
# saves it in an output file with a new name.

# The FIX_ONLY code solves some quirk with
# the Rigol PNG format which causes imagemagick
# to hiccup. Simply reading it and saving it
# in Python solves the problem.

import sys
from PIL import Image, ImageDraw, ImageFont

def fix_only(argv):
  if len(argv) < 2:
    print('Usage: rigol-fix-png <fname>')
    exit(0)
  fname = argv[1]
  outfname = 'fix-' + fname
  img = Image.open(fname)
  img.save(outfname)

fontdir = '/Users/rclott/fonts/d2codingfont/D2Coding-Ver1.3.2-20180524/D2Coding/'
fontfile = 'D2Coding-Ver1.3.2-20180524.ttf'
fontpath = fontdir + fontfile

def main(argv):
  if len(argv) < 4:
    print('Usage: rigol-fix-png <input-file> <label> <output-file>')
    exit(0)
  fname_in = argv[1]
  label = argv[2].upper()
  fname_out = argv[3]
  img = Image.open(fname_in)
  w,h = img.size
  font = ImageFont.truetype("Keyboard", 28)
  draw = ImageDraw.Draw(img)
  #label = 'xmt-075'.upper()
  xpos = 0.125 * w
  ypos = 0.75 * h
  xoff = 7
  yoff = 7
  textposn = (xpos, ypos)
  box = draw.textbbox( textposn, label, font=font ) 
  bbox = ( box[0]-xoff, box[1]-yoff, box[2]+xoff, box[3]+yoff )
  draw.rectangle(bbox, fill='gray', outline='gold', width=3)
  draw.text( textposn, label , fill='white' , font=font)
  img.save(fname_out)

if __name__ == "__main__":
  #main(sys.argv)
  fix_only(sys.argv)
