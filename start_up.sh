#!/bin/bash
docker build -t pii-anonymizer ./container
./scripts/serve_local.sh pii-anonymizer