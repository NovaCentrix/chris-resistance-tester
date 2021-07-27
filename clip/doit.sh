#!/bin/bash

INFILES='../sweeps'
# counter=0
# for f in $INFILES/*-xmt-*.png; do
#   let counter++
#   fname=$(basename $f)
#   oname=$(echo $fname | sed "s/-[0-9][0-9][0-9]-ohms.png//")
#   res=$(echo $fname | sed "s/^rsweep-//" | sed "s/-ohms\.png//")
#   ./rigol-fix-png.py $f $res $oname-$(printf "%03d" $counter).png
#   echo $f $res $oname-$(printf "%03d" $counter).png
# done
# ffmpeg -framerate 2 -i rsweep-xmt-%03d.png -c:v libx264 -r 30 xmt.mp4

counter=0
for f in $INFILES/*-rcv-*.png; do
  let counter++
  fname=$(basename $f)
  oname=$(echo $fname | sed "s/-[0-9][0-9][0-9]-ohms.png//")
  res=$(echo $fname | sed "s/^rsweep-//" | sed "s/-ohms\.png//")
  ./rigol-fix-png.py $f $res $oname-$(printf "%03d" $counter).png
  echo $f $res $oname-$(printf "%03d" $counter).png
done
ffmpeg -framerate 2 -i rsweep-rcv-%03d.png -c:v libx264 -r 30 rcv.mp4
