#!/bin/bash

dir=`dirname "$0"`
chappie_root=$(realpath `dirname "$0"`)/..

work_dir=$1
for bench in $work_dir/*; do
  for rate in $bench/*; do
    for run in $rate/*; do
      python3 $chappie_root/src/python/analysis --work-directory $work_dir
    done
  done
done

for analysis in $dir/analysis/*; do
  $analysis $work_dir
done
