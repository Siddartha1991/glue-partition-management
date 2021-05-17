# glue-catalog-partition-management

   ## Version  -1.0
   Git Repo trigger CICD pipelines for Lambda Code Deployments and AWS Layers Package Deployments.

   Lambda function Name - 'environment-208385-catalog-glue-partition-mgmt-process'
   Layers Package - python package 'aws-wrangler'

   ## Description:
   glue-catalog-partition-management will help manage partitions for Glue Catalog Tables in all RAW databases.

   ## Prerequisites:
   Should have
   1) Knowledge/Hands-on with git hub and git cli is required.\
        refer - [Git](https://docs.github.com/en) 
   2) Knowledge on different layers in the data lake. \
       refer - shorty/dllayers
   3) Understanding of CircleCi and HAL.
   4) Git cli installed on the machine.

   
   ## Overview of the Deployment
   
   1) Changes to this Git Repo will trigger Circle CI pipelines for deploying code to the Lambda Function and adding newer version to the AWS Layers which will later be attached to the Lambda Function
   2) build.sh script will packages all the new and modified code components and artifacts and  publish them to HAL container.
   4) deploy.sh script will execute the python script to push code upgrades to AWS Lambda and/or Increment AWS Layer version and attach it to Lambda
   
   ## Git Repo Structure
    
        root-
              | - modules/
              | - tests/
              | - main.py
              | - requirements.txt
              | - .hal9000.yml
              | - .circleci/config.yml
              | - build.sh
              | - deploy.sh
              | - README.md
              | - CHANGELOG.MD
              | - teams_notiy_on_fail.sh
              | - update_env_sha_val.sh


   ## Deep dive details of each components in the git repo and process:
   
  #### requirements.txt: 
  This file contains all the python packages that need to be installed, packaged and deployed into AWS Layer. 
  These python packages are needed for the core lambda logic to run successfully.
                              
  #### modules: 
  This folder contains different code modules for implementing of various functionalities of the process.  
  AwsClientObj.py - Class creates boto3 client objects for S3 and Glue.  
  GlueAPISetup.py - Class has Various Methods with Processing, formatting and calling Glue API calls needed in the process.  
  ProcessLogger.py - Class has logger modules and objects setup.  
  S3PrefixGeneration.py - Class has various methods with to process and format information to generate S3 Prefixes for new partitions.

  #### tests: 
  This folder contains all the test scripts. These unit test scripts will be run during the Circle CI pipeline. Only if all unit tests are successful , the circle CI pipeline deploys the code to AWS  
  test_glue_api_setup.py - unit tests for Glue API processing methods.  
  test_s3prefixgeneration.py - unit tests for s3 prefix generation methods.  
  test_inputs.py - contains inputs and expected outputs for some of the unit test methods.
  
  #### main.py: 
  This file will act as a starting point for the code with the Lambda_Handler function in it. It will also get the Database information from Parent Lambda Function
  
  #### .hal9000.yml:
  This file will contain Hal required configuration (like environment variable and docker image to deploy our services) to run the deployment.
  
  #### .circleci/config.yml:
  This file will contain circleci configuration that drives the build and integration to HAL to deploy the artifacts. 
  
  ####  build.sh:
  This script is executed in the circleci container during the build process. It will package all the code modules and moves them into publish folder for Artifact building.
  
  #### deploy.sh:
  This script will either or both of below
  1. If changes occur in requirements.txt - pip install those changes and package them into multiple zip files of size < 35M. Then it will do a AWS CLI call to push those changes to AWS Layers as newer versions. 
  Next, attach these latest version of Layers to the Lambda Function.
  2. Code in AWS modules & main.py will be deployed to AWS Lambda Function.
  
  #### teams_notiy_on_fail.sh:
  This script will send circleci pipeline failures at any step to microsoft team channel which can configured in the circleci project environment variables.
  
  ## How to deploy a Code Changes in each environment:
  Note 1 - **Do frequent git fetch and pull from the master to avoid any conflicts**.\
  Note 2 - **Make sure local changes are committed first before doing the git fetch and pull otherwise local changes will be overwritten**.    
  
 ### How Code Changes are deployed in dev/beta environment?
   
 1) Create a pull request from the working branch.
 2) Once the PR is reviewed and merged then Circle CI pipeline will trigger to deploy the code in dev and beta environment.
   
    
 ### How Code Changes are deployed in prod environment?
   
 1) Prod deployments will have an additional approval step in the Circle CI pipeline.
 2) On approval, code will be deployed to Prod environment.
      
   
   
   
  

  

  
   
   
        
          
