#!/bin/bash

this_dir=`git rev-parse --show-toplevel`
cd $this_dir
cd containers

echo git dir: $this_dir
pwd
ls -ltrh

rm -rf python_analysis.sif
sudo singularity build python_analysis.sif python_analysis.def

rsync -avh --progress ./python_analysis.sif rocks:/data/eliza2/g2/users/labounty/