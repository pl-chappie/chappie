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

dir=$(realpath `dirname "$0"`)
chappie_root=$dir/../..
dacapo_command=$dir/dacapo.sh

data_root=$1
mkdir $data_root
data_root=$data_root/calmness
mkdir $data_root

calm_data_root=$data_root/calm
mkdir $calm_data_root

profile_data_root=$data_root/profile
mkdir $profile_data_root

iters=10
rates=(1 0 2 4 8 16 32 64 128 256 512)

cases=$(cat $chappie_root/fse2020/experiment-sizes.txt)
set -f; IFS=$'\n'
set +f;

for case in ${cases[@]}; do
  bench=${case%%' '*}
  size=${case#*' '}
  run_calmness_experiment
done
