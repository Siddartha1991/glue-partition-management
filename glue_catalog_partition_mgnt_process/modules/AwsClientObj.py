import boto3
from botocore.exceptions import UnknownServiceError
from modules.ProcessLogger import setup_logging

logger = setup_logging().getLogger(__name__)
class AwsClientObj:
    def __init__(self):
        pass

    def create_aws_client_obj(self,aws_service):
        try:
            aws_client = boto3.client(aws_service,region_name='us-east-2')
            return aws_client
        except UnknownServiceError as e:
            logger.error("Incorrect AWS Service Name Provided - {}".format(aws_service))
            raise e
        except Exception as e:
            logger.error("Unknown Exception Found")
            raise e