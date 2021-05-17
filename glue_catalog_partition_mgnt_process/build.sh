#!/bin/bash
# set -eo pipefail
mkdir -p publish

mkdir -p publish/code
mkdir -p .bin
echo "Copying code ..."
cp -R modules/ .bin/
cp main.py .bin/

echo "Zipping files ..."
cd .bin && zip -r ../publish/code/glue-partition-processing-lambda.zip *
cd ..

HEAD=$(echo $CIRCLE_SHA1 | cut -c -7)
echo "$HEAD"
pattern="^requirements"
diff_result=$(git diff-tree --no-commit-id --name-status -r $HEAD | grep -e "^A\|^M\|^U" | awk '{print $2}' | grep -e "$pattern")
echo "$diff_result"

if [ ! -z "$diff_result" ]
then
   mkdir -p publish/layer
   #package layer
   echo "Copying requirements.txt file ..."

   cp requirements.txt ./publish/layer
fi