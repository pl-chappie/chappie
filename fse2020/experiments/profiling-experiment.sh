#!/bin/bash

function run_profiling_experiment {
  mkdir ${data_root}/${bench}
  ln -s $(realpath $ref_data/${bench}/${rate}) ${data_root}/${bench}/0
  python3 $chappie_root/src/python/analysis --work-directory ${data_root}/${bench}/0
  for i in `seq 1 $cold_iters`; do
    work_dir=${data_root}/${bench}/${i}
    rm -rf $work_dir
    mkdir $work_dir
    $dacapo_command $work_dir "-Dchappie.rate=$rate" $bench "--size $size --iterations $hot_iters"
    python3 $chappie_root/src/python/analysis --work-directory $work_dir
    corr=$(python3 $experiment_root/convergence-check.py -d ${data_root}/${bench})
    if (( $(echo "$corr >= $threshold" | bc -l ) )); then
      break
    fi
  done
}

experiment_root=$(realpath `dirname "$0"`)
chappie_root=$experiment_root/../..
dacapo_command=$experiment_root/dacapo.sh

data_root=$1
mkdir $data_root
ref_data=$data_root/calmness/profile
data_root=$data_root/profiling
mkdir $data_root

threshold=0.98
hot_iters=10
cold_iters=10

cases=$(cat $1/.calm-rates)
set -f; IFS=$'\n'
set +f;

for case in ${cases[@]}; do
  bench=${case%%' '*}
  tmp=${case#*' '}
  size=${tmp%%' '*}
  rate=${tmp##*' '}
  run_profiling_experiment
done
