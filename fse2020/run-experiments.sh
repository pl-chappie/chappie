#!/bin/bash

dir=`dirname "$0"`

if [ $1 -z ]; then
  work_dir='chappie-logs'
elif
  work_dir=$1
fi

$dir/experiments/calmness-experiment.sh $work_dir
$dir/experiments/profile-experiment.sh $work_dir
$dir/data-processing.sh $work_dir/profile
