#!/bin/bash

dir=`dirname "$0"`
work_dir=./chappie-data
mkdir $work_dir
mkdir $work_dir/plots
echo "testing message" > $work_dir/plots/log.txt
cat $work_dir/plots/log.txt

# calmness experiment
# $dir/experiments/calmness-experiment.sh $work_dir
# python3 $dir/experiments/calmness-check.py -d $work_dir

# profile experiment
# $dir/experiments/profiling-experiment.sh $work_dir
# $dir/plotting.sh $work_dir
