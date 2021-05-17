terragrunt_source = "git::https://git.rockfin.com/terraform/aws-iam-tf.git//modules/inline-policy-iam?ref=2.3.0" # Substitute X with the latest release

#-----------------------------------------------------
#--------------------IAM Variables--------------------
#-----------------------------------------------------

aws_region      = "us-east-2"
arn_of_resource = ""
role_names      = ["role-beta-208385-catalog-glue-partition-mgmt-process-us-east-2"] # Fill out with the IAM role names, comma separated, you'd like to have access to the KMS key. NOT THE ARN, but the name, ie "role-test-999999-webapi"
aws_resource    = "gluecatalogpolicy"