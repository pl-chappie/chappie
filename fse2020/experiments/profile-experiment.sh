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

hot_iters=4

cold_iters=3
rate=8
benchs=(
  biojava
  jython
)
# size=default
size=default

for bench in ${benchs[@]}; do
  run_profiling_experiment
done

rate=16
benchs=(
  xalan
)
# size=default

for bench in ${benchs[@]}; do
  run_profiling_experiment
done

rate=128
benchs=(
  avrora
)
# size=large

for bench in ${benchs[@]}; do
  run_profiling_experiment
done

rate=8
benchs=(
  batik
)
# size=large

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
# size=large

for bench in ${benchs[@]}; do
  run_profiling_experiment
done

rate=16
benchs=(
  graphchi
)
# size=huge

for bench in ${benchs[@]}; do
  run_profiling_experiment
done
