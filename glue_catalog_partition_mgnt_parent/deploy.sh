#!/bin/bash

echo "---- uploading lambda code -------"

aws lambda update-function-code --region us-east-2 --function-name ${LAMBDA_NAME} --zip-file fileb://${PACKAGE_NAME}

