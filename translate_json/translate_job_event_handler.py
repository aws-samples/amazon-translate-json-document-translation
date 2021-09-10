## Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
## SPDX-License-Identifier: MIT-0

import json
import logging
import os
import sys
import xmltodict
from urllib.parse import urlparse
from botocore.exceptions import ClientError
from helper import FileHelper,S3Helper

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def processRequest(request):
    output = ""
    logger.debug("request: {}".format(request))
    up = urlparse(request["s3uri"], allow_fragments=False)
    accountid = request["accountId"]
    jobid =  request["jobId"]
    bucketName = up.netloc
    objectkey = up.path.lstrip('/')
    # choose the base path for iterating within the translated files for the specific job
    basePrefixPath = objectkey  + accountid + "-TranslateText-" + jobid + "/"
    languageCode = request["langCode"]
    logger.debug("Base Prefix Path:{}".format(basePrefixPath))
    # Filter only the translated XML files for processing
    objs = S3Helper().getFilteredFileNames(bucketName,basePrefixPath,"xml")
    for obj in objs:
        try:
            content = S3Helper().readFromS3(bucketName,obj)
            logger.debug(content)
            #Convert the XML file to Dictionary object
            data_dict = xmltodict.parse(content)
            #Generate the Json content from the dictionary
            data_dict =  data_dict["all"]
            flatten_dict = {k: (data_dict[k]["item"] if (isinstance(v,dict) and len(v.keys()) ==1 and "item" in v.keys())  else v) for (k,v) in data_dict.items()}
            json_data = json.dumps(flatten_dict,ensure_ascii=False).encode('utf-8')
            logger.debug(json_data)
            newObjectKey = "output/{}.json".format(FileHelper.getFileName(obj))
            #Write the JSON object to the S3 output folder within the bucket
            S3Helper().writeToS3(json_data,bucketName,newObjectKey)   
            output = "Output Object: {}/{}".format(bucketName, newObjectKey)
            logger.debug(output)
        except ValueError:
            logger.error("Error occured loading the json file:{}".format(obj))
        except ClientError as e:
            logger.error("An error occured with S3 bucket operations: %s" % e)
        except :
            e = sys.exc_info()[0]
            logger.error("Error occured processing the xmlfile: %s" % e)
    objs = S3Helper().getFilteredFileNames(bucketName,"xmlin/","xml")
    if( request["delete_xmls"] and request["delete_xmls"] == "true") :
        for obj in objs:
            try:
                logger.debug("Deleting temp xml files {}".format(obj))
                S3Helper().deleteObject(bucketName,obj)
            except ClientError as e:
                logger.error("An error occured with S3 bucket operations: %s" % e)
            except :
                e = sys.exc_info()[0]
                logger.error("Error occured processing the xmlfile: %s" % e)

def lambda_handler(event, context):
    logger.setLevel(logging.DEBUG)
    logger.info("event: {}".format(event))
    request = {}
    statusCode = "200"
    message ="success"
    request["delete_xmls"] = os.environ["DELETE_XMLS"]
    try:
        message = json.loads(event['Records'][0]['Sns']['Message'])
        request["s3uri"] =  message['S3OutputLocation']
        request["jobId"] = message['JobId']
        request["jobName"] = message['JobName']
        status = message['JobStatus']
        request["langCode"] = message['langCode'][0]
        request["accountId"] = context.invoked_function_arn.split(":")[4]
        if status == "COMPLETED" :
            processRequest(request)
        elif status in ["FAILED", "COMPLETED_WITH_ERROR"]:
            statusCode ="500"
            message = "Translation Job failed"
            logger.warn("Job ID {} failed or completed with errors, exiting".format(request["jobId"]))
    except ValueError:
        statusCode ="500"
        message = "Error converting the XML document"
        logger.error("Error occured loading the json from event:{}".format(event))
    return {
            "statusCode": statusCode,
            "body": json.dumps(message)
        }