import os
from modules.AwsClientObj import AwsClientObj
from modules.GlueApiSetup import GlueApiSetup
from modules.ProcessLogger import setup_logging
from modules.S3PrefixGeneration import S3PrefixGeneration

logger = setup_logging().getLogger(__name__)



def lambda_handler(event, context):
    
    logger.info("IN MAIN FUNCTION..")
    
    logger.info("creating AWS Boto Objects..")
    obj = AwsClientObj()
    glue_client = obj.create_aws_client_obj("glue")
    s3_client = obj.create_aws_client_obj("s3")

    glue_setup_obj = GlueApiSetup(glue_client)
    s3_prefix_obj = S3PrefixGeneration(s3_client)
    
    logger.info("glue s3 setup objects created")

    # Iterate through parsed list of tables
    for parse_table_dict in glue_setup_obj.parse_table_info(event['tables']):
        logger.info("Database: {0}, Table_Name:{1}".format(event['database_name'],parse_table_dict['table_name']))
        # makes a call to s3 bucket and get latest partition for table from last 2 days based on part keys
        s3_prefix_list = s3_prefix_obj.get_s3partition_list(parse_table_dict)
        logger.info("S3PrefixList: {0}".format(s3_prefix_list))
        if len(s3_prefix_list) > 0:
            # Parse and create partition input list for batch api call to run
            partition_input_list = glue_setup_obj.batch_partition_input_list(s3_prefix_list, parse_table_dict)
            if len(partition_input_list) > 0:
                # Batch Create Partition API call - can add upto 100 partitions for a table in a single run
                create_partition_response = glue_setup_obj.create_batch_partition_call(event['database_name'],parse_table_dict['table_name'],partition_input_list)
        else:
            logger.info("S3PrefixList is empty")