#!/bin/bash

IMAGE_NAME=${1:-'pii-anonymizer'}
PORT=${2:-8989}
docker build -t ${IMAGE_NAME} ./container
./scripts/serve_local.sh ${IMAGE_NAME} ${PORT}
