#!/bin/sh -l

echo "Hello entrypoint $1"
time=$(date)
echo ::set-output name=time::$time


git --version