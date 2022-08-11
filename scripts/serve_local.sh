#!/bin/sh

image=$1
port=$2

docker run -v $(pwd)/test_dir:/opt/ml -p ${port}:8080 --rm ${image} serve