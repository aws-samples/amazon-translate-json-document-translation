#!/bin/bash
set -eo pipefail
ARTIFACT_BUCKET=$(cat bucket-name.txt)
TEMPLATE=translate-json-template.yaml
sam build -t $TEMPLATE
cd .aws-sam/build

sam package --debug  --s3-bucket $ARTIFACT_BUCKET --output-template-file translate-json-template-cf.yml
sam deploy --debug --template-file translate-json-template-cf.yml --stack-name translate-json-stack --capabilities CAPABILITY_NAMED_IAM
