#!/bin/bash

dir=`dirname "$0"`
work_dir=./chappie-data
mkdir $work_dir

# calmness experiment
$dir/experiments/calmness-experiment.sh $work_dir
python3 $dir/experiments/calmness-check.py -d $work_dir

# profile experiment
$dir/experiments/profiling-experiment.sh $work_dir
$dir/plotting.sh $work_dir

ls $work_dir
ls $work_dir/plots
