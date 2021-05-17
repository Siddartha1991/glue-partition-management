terragrunt_source = "git::https://git.rockfin.com/terraform/aws-lambda-tf.git?ref=3.6.0"

# ---------------------------------------------------------------------------------------------------------------------
# Required variables for AWS
# ---------------------------------------------------------------------------------------------------------------------

aws_region     = "us-east-2"
aws_account_id = "609457042523"

# ---------------------------------------------------------------------------------------------------------------------
# Standard Module Required Variables
# ---------------------------------------------------------------------------------------------------------------------

app_id           = "208385"
application_name = "catalog-glue"
environment      = "beta"

development_team_email        = "siddartharaochennur@quickenloans.com"
infrastructure_team_email     = "siddartharaochennur@quickenloans.com"
infrastructure_engineer_email = "siddartharaochennur@quickenloans.com"

# ---------------------------------------------------------------------------------------------------------------------
# Infrastructure Tags
# ---------------------------------------------------------------------------------------------------------------------

app_tags = {
  hal-app-id = "7964"
}


# ---------------------------------------------------------------------------------------------------------------------
# Infrastructure Variables
# ---------------------------------------------------------------------------------------------------------------------

lambda_name  = "partition-mgmt-parent"
#cloudwatch_event_rule_name = "hourly_schedule"
#lambda_security_group_id = "sg-0c68a71f7f0e9c751"

#vpc_id = "vpc-09ed6cf29e51246d5"
#vpc_subnets = ["subnet-0343c599899be71cb","subnet-0f174fde04c72740e","subnet-0be879b8891441e76"]

memory_size = "128"

environment_variables = {
  PROCESS_LAMBDA = "beta-208385-catalog-glue-partition-mgmt-process"
}
lambda_timeout = "800"

## Due to IAM role creation utilizing the lambda name for identification,
## the application_name + lambda_name totaled together
## cannot exceed 47 characters.


## Uncomment if you will provide your own code in a zip format
lambda_runtime = "python3.8"
lambda_handler = "lambda_function.lambda_handler"
