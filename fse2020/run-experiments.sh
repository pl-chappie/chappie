#!/bin/bash

dir=`dirname "$0"`
data_dir=$dir/../fse2020-test
# data_dir=~/chappie-data
mkdir $data_dir

# calmness experiment
$dir/experiments/calmness-experiment.sh $data_dir
python3 $dir/experiments/calmness-check.py -d $data_dir

# profile experiment
$dir/experiments/profile-experiment.sh $data_dir
python3 $dir/experiments/convergence-check.py -d $data_dir
