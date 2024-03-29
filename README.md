# Translating JSON documents using Amazon Translate


## About
This project contains source code and supporting files for a serverless pipeline for translating JSON documents using Amazon Translate that you can deploy with the SAM CLI. It includes the following files and folders.

- translate_json - Code for the application's Lambda functions.
- translate-json-template.yaml - A template that defines the application's AWS resources.

The application uses several AWS resources, including AWS Lambda functions, Amazon Simple Storage Service and Amazon EventBridge Rules. These resources are defined in the `translate-json-template.yaml` file in this project. 

Important: this application uses Amazon Translate and there are costs associated with this service after the Free Tier usage - please see the   [Amazon Translate pricing page](https://aws.amazon.com/translate/pricing/) for details.

### Reference
[Translating JSON documents with Amazon Translate](https://aws.amazon.com/blogs/machine-learning/translating-json-documents-using-amazon-translate/) 


## Solution Architecture
![](solution.jpg)
<img src="solution.png" />

## Building and Deploying the application

### Requirements

* AWS CLI - Installed and Configured with a valid profile [Install the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)
* The Bash shell. For Linux and macOS, this is included by default. In Windows 10, you can install the [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10) to get a Windows-integrated version of Ubuntu and Bash.

### Setup
Download or clone this repository.

    $ git clone git@github.com:aws-samples/amazon-translate-json-document-translation.git
    $ cd amazon-translate-json-document-translation

To create a new bucket for deployment artifacts, run `create-bucket.sh`.

    $ ./create-bucket.sh
    make_bucket: lambda-artifacts-a5e491dbb5b22e0d

### Deploy

To deploy the application, run `deploy.sh`.

    $ ./deploy.sh
    BUILD SUCCESSFUL in 1s
    Successfully packaged artifacts and wrote output template to file out.yml.
    Waiting for changeset to be created..
    Successfully created/updated stack - translate-json-stack

This script uses AWS CloudFormation to deploy the Lambda functions and an IAM role. If the AWS CloudFormation stack that contains the resources already exists, the script updates it with any changes to the template or function code.

## How it works
* Deploy the stack  with required parameters (`SourceLanguageCode`, `TargetLanguageCode` and `TriggerFileName`)
* Upload JSON files in the `input` folder of the created Amazon S3 bucket.
* Upload the 0-byte file with name matching the `TriggerFileName` parameter in the `input` folder
* The solution will trigger and after few minutes , you will see the translated JSON files in `output` folder in the same bucket


### Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name translate-json-stack
```

## License

This solution is licensed under the MIT-0 License. See the LICENSE file.


