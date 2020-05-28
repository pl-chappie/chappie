#!/bin/bash

function run_profiling_experiment {
  mkdir ${data}/${bench}
  for i in `seq 1 $cold_iters`; do
    work_dir=${data_root}/${bench}/${i}
    rm -rf $work_dir
    mkdir $work_dir
    $dacapo_command $work_dir "-Dchappie.rate=$rate" $bench "--size $size --iterations $hot_iters"
  done
}

chappie_root=$(realpath `dirname "$0"`)/../..
experiment_root=$chappie_root/experiments
dacapo_command=$experiment_root/dacapo.sh

data_root=$1/profile
mkdir $data_root

hot_iters=10

cold_iters=4
rate=8
benchs=(
  biojava
  jython
)
size=default

for bench in ${benchs[@]}; do
  run_profiling_experiment
done

rate=16
benchs=(
  xalan
)
size=default

for bench in ${benchs[@]}; do
  run_profiling_experiment
done

rate=128
benchs=(
  avrora
)
size=large

for bench in ${benchs[@]}; do
  run_profiling_experiment
done

rate=8
benchs=(
  batik
)
size=large

for bench in ${benchs[@]}; do
  run_profiling_experiment
done

rate=16
benchs=(
  eclipse
  h2
  pmd
  sunflow
  tomcat
)
size=large

for bench in ${benchs[@]}; do
  run_profiling_experiment
done

rate=16
benchs=(
  graphchi
)
size=huge

for bench in ${benchs[@]}; do
  run_profiling_experiment
done
