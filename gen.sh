#!/bin/sh

configurations=("5 1 10" "5 2 10" "5 3 10" "10 1 10" "10 2 10" "10 3 10" "15 1 10" "15 2 10" "15 3 10" "25 1 10" "25 2 10" "25 3 10" "50 1 10" "50 2 10" "50 3 10")

for x in "${configurations[@]}"; do
    echo $x
done | xargs -P0 -i sh -c 'set {}; mkdir -p data/$1x$2x$3/star && for i in $(seq 1 1000); do name=$(printf %06d $i); ../vbmap/vbmap --num-vbuckets=1024 --num-nodes=$1 --num-replicas=$2 --num-slaves=$3 --output-format=ext-json > data/$1x$2x$3/star/$name || exit 255; done' || exit 1

ls -1d data/* | xargs -i -P0 sh -c 'python2 ./vbmap_sim.py -o {} {}/* || exit 255' || exit 1
