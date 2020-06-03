#!/bin/bash

dir=`dirname "$0"`
chappie_root=$(realpath `dirname "$0"`)/..

work_dir=$1
for bench in $work_dir/*; do
  for run in $bench/*; do
    python3 $chappie_root/src/python/analysis --work-directory $run
  done
done
