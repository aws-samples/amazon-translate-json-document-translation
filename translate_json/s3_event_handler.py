## Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
## SPDX-License-Identifier: MIT-0

import json
import logging
import os
import time
from botocore.exceptions import ClientError
from json2xml import json2xml
from helper import FileHelper,S3Helper,AwsHelper


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
def startTranslationJob(bucketName, sourceCode, destCode,access_role):
    translate = AwsHelper().getClient('translate')
    try: 
        millis = int(round(time.time() * 1000))
        response = translate.start_text_translation_job(
            JobName="TranslateJob-json-{}".format(millis),
            InputDataConfig={
                'S3Uri': "s3://{}/xmlin/".format(bucketName),
                'ContentType': 'text/html'
            },
            OutputDataConfig={
                'S3Uri': "s3://{}/xmlout/".format(bucketName)
            },
            DataAccessRoleArn=access_role,
            SourceLanguageCode=sourceCode,
            TargetLanguageCodes=[destCode]
        )
        print(response["JobId"])
    except ClientError as e:
        logger.error("An error occured starting the Translate Batch Job: %s" % e)
def processRequest(request):
    output = ""
    logger.info("request: {}".format(request))

    bucketName = request["bucketName"]
    sourceLanguageCode = request["sourceLanguage"]
    targetLanguageCode = request["targetLanguage"]
    access_role = request["access_role"]
    triggerFile = request["trigger_file"]
    try:
        # Filter only the JSON files for processing
        objs = S3Helper().getFilteredFileNames(bucketName,"input/","json")
        for obj in objs:
            try:
                content = S3Helper().readFromS3(bucketName,obj)
                logger.debug(content)
                jsonDocument = json.loads(content)
                print(jsonDocument)
                # Convert the JSON document into XML
                outputXML = json2xml.Json2xml(jsonDocument, attr_type=False).to_xml()
                logger.debug(outputXML)
                newObjectKey = "xmlin/{}.xml".format(FileHelper.getFileName(obj))
                # Store the XML in the S3 location for Translation
                S3Helper().writeToS3(str(outputXML),bucketName,newObjectKey)   
                output = "Output Object: {}/{}".format(bucketName, newObjectKey)
                logger.debug(output)
                # Rename the JSON files to prevent reprocessing
                S3Helper().renameObject(bucketName,obj,"{}.processed".format(obj))
            except ValueError:
                logger.error("Error occured loading the json file:{}".format(obj))
            except ClientError as e:
                logger.error("An error occured with S3 Bucket Operation: %s" % e)
        # Start the translation batch job using Amazon Translate
        startTranslationJob(bucketName,sourceLanguageCode,targetLanguageCode,access_role)
        S3Helper().deleteObject(bucketName,"input/{}".format(triggerFile))
    except ClientError as e:
        logger.error("An error occured with S3 Bucket Operation: %s" % e)

def lambda_handler(event, context):
    logger.setLevel(logging.DEBUG)
    logger.info("event: {}".format(event))
    request = {}
    request["bucketName"] = event['Records'][0]['s3']['bucket']['name']
    request["sourceLanguage"] = os.environ['SOURCE_LANG_CODE']
    request["targetLanguage"] = os.environ['TARGET_LANG_CODE']
    request["access_role"] = os.environ['S3_ROLE_ARN']
    request["trigger_file"] = os.environ['TRIGGER_NAME']
    processRequest(request)
    return {
        "statusCode": 200,
        "body": json.dumps('success')
    }
