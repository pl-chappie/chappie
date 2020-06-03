#!/bin/bash

function run_calmness_experiment {
  mkdir ${calm_data_root}/${bench}
  mkdir ${profile_data_root}/${bench}
  for rate in ${rates[@]}; do
    if [ $rate == "0" ]; then
      work_dir=${calm_data_root}/${bench}
      rm -rf $work_dir
      mkdir $work_dir
      $dacapo_command $work_dir "-Dchappie.rate=0" $bench "--size $size --iterations $iters"
    else
      work_dir=${profile_data_root}/${bench}/${rate}
      rm -rf $work_dir
      mkdir $work_dir
      freq_rate=$((512 / $rate))
      $dacapo_command $work_dir "-Dchappie.rate=$rate -Dchappie.freq=$freq_rate" $bench "--size $size --iterations $iters"
    fi
  done
}

experiment_root=$(realpath `dirname "$0"`)
chappie_root=$experiment_root/../..
dacapo_command=$experiment_root/dacapo.sh

data_root=$1
mkdir $data_root
data_root=$data_root/calmness
mkdir $data_root

calm_data_root=$data_root/calm
mkdir $calm_data_root

profile_data_root=$data_root/profile
mkdir $profile_data_root

iters=4
rates=(0 1 2 4 8 16 32 64 128 256 512)
size=default

benchs=(
  biojava
  jython
  xalan
)
# size=default

for bench in ${benchs[@]}; do
  run_calmness_experiment
done

benchs=(
  avrora
  batik
  eclipse
  h2
  pmd
  sunflow
  tomcat
)
# size=large

for bench in ${benchs[@]}; do
  run_calmness_experiment
done

benchs=(
  graphchi
)
# size=huge

for bench in ${benchs[@]}; do
  run_calmness_experiment
done
