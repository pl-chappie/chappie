#!/bin/bash

chappie_root=$(realpath `dirname "$0"`)/..
python3 $chappie_root/src/python/run "$@"
