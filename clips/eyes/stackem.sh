#!/bin/bash

INFILES=(
  'eye-000.png'
  'eye-050.png'
  'eye-100.png'
  'eye-150.png'
  'eye-200.png'
  'eye-250.png'
  'eye-300.png'
)

####    echo ${INFILES[*]}
####    outfiles=()
####    for f in ${INFILES[*]}; do
####      outfiles+=("out-$f")
####    done
####    echo ${outfiles[*]}
####    exit

# make background
convert -size 800x480 xc:#c0c0c0 back.png

#outfiles=('back.png')
outfiles=()
for f in ${INFILES[*]}; do
  echo $f
  ohms=$(echo $f | grep -o "[0-9][0-9][0-9]")
  fixfile=$(echo "fix-$f")
  ofile="out-$(printf "%03d" $ohms).png"
  ../rigol-fix-png.py $f
  convert $fixfile -fuzz 25% -transparent black $ofile
  outfiles+=("$ofile")
done

convert $(echo ${outfiles[*]}) -gravity center -background black -layers flatten result.png

#### 
####  convert fix-test1.png -fuzz 25% -transparent black out1.png
####  convert fix-test3.png -fuzz 25% -transparent black out3.png
####  ll out*
####  cp eye-020.png test0.png
####  ../rigol-fix-png.py test0.png
####  mv fix-test0.png out0.png
####  convert out0.png out1.png out2.png out3.png  -gravity center -background None -flatten layers all.png 
####  convert out0.png out1.png out2.png out3.png  -gravity center -background None -layers flatten all.png
####  start all.png
####  ll
####  history > stackem.sh



# INFILES='../sweeps'
# 
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

## counter=0
## for f in $INFILES/*-rcv-*.png; do
##   let counter++
##   fname=$(basename $f)
##   oname=$(echo $fname | sed "s/-[0-9][0-9][0-9]-ohms.png//")
##   res=$(echo $fname | sed "s/^rsweep-//" | sed "s/-ohms\.png//")
##   ./rigol-fix-png.py $f $res $oname-$(printf "%03d" $counter).png
##   echo $f $res $oname-$(printf "%03d" $counter).png
## done
## ffmpeg -framerate 2 -i rsweep-rcv-%03d.png -c:v libx264 -r 30 rcv.mp4
