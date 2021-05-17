#!/bin/bash

echo "---- uploading lambda layer zip file -------"
export PKG_DIR="python"

rm -rf ${PKG_DIR} && mkdir -p ${PKG_DIR}
if [[ -d "code" ]]
then
    echo "---- uploading lambda code -------"
    aws lambda update-function-code --region us-east-2 --function-name ${LAMBDA_NAME} --zip-file fileb://code/${PACKAGE_NAME}
fi
if [[ -d "layer" ]]
then
    echo "---- uploading layer -------"
    pip install -r layer/requirements.txt -t ${PKG_DIR}
    rm -rf python/boto*
    rm -r python/pandas/tests/*
    rm -r python/pyarrow/tests/*
    zip -r ${LAYER_PACKAGE_NAME} ./python
    zipsplit -n 35943040 ${LAYER_PACKAGE_NAME}
    echo "Zip Split Completed"
    ls -lrt
    LAYER_LIST=""
    for obj in $(ls *.zip)
        do
            if [[ $obj != ${LAYER_PACKAGE_NAME} ]]
            then
            echo "$obj"
            LAYER_NAME="$(echo $obj | cut -d'.' -f1)"
            echo "$LAYER_NAME"
            layerarn=$(aws lambda publish-layer-version --region us-east-2 --layer-name ${LAYER_NAME} --zip-file fileb://${obj} --query 'LayerVersionArn' --output text)
            echo "$layerarn"
            LAYER_LIST+="$layerarn "
            fi
        done
    echo "---- Layers Attached to Lambda -------"
    echo "$LAYER_LIST"
    aws lambda update-function-configuration --region us-east-2 --function-name ${LAMBDA_NAME} --layers $LAYER_LIST
fi