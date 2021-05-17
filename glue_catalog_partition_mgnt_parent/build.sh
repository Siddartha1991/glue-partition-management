#!/bin/bash
# set -eo pipefail

mkdir -p .bin
mkdir -p publish
echo "Copying code ..."
cp lambda_function.py .bin/

echo "Zipping files ..."
cd .bin && zip -r ../publish/glue-partition-parent-lambda.zip *
cd ..