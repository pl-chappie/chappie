#!/bin/bash

dir=`dirname "$0"`

work_dir=$1
for script in $dir/analysis/*; do
  python3 $script -work-directory $work_dir
done
