import sys
import copy
import botocore
from botocore.exceptions import ClientError
from modules.ProcessLogger import setup_logging

logger = setup_logging().getLogger(__name__)

class GlueApiSetup:

    def __init__(self,glue_client):
        self.glue_client = glue_client

    def parse_table_info(self,res):
        '''
        Parse Table List to fetch table name, storage description and partition keys list

        Parameters:
        res : table list info from get tables api call

        Return:
        yield in an iterative fashion..

        table: table name 
        storage_desc: storage description of the table
        part_keys: partition list 
        '''
        bucket_name = ""
        for i in range(0,len(res["TableList"])):
            parse_table_dict = {}
            logger.info("********* in parse table info ********* table_name: {}".format(res['TableList'][i]['Name']))
            if('PartitionKeys' in res["TableList"][i].keys()):
                len_part_keys = len(res["TableList"][i]['PartitionKeys'])
                if(len_part_keys != 0):
                    storage_desc = res["TableList"][i]['StorageDescriptor']
                    table = res["TableList"][i]['Name']

                    location = res["TableList"][i]['StorageDescriptor']['Location']

                    if(not location.endswith('/')):
                        location += '/'

                    location_split = location.split('/')

                    parse_table_dict['table_prefix_name'] = location_split[-2]
                    parse_table_dict['bucket_name'] = location_split[2]
                    parse_table_dict['head_prefix'] = '/'.join(location_split[3:-2]) + "/"
                    parse_table_dict['storage_desc'] = storage_desc
                    parse_table_dict['table_name'] = table

                    part_keys = []
                    for i in res["TableList"][i]['PartitionKeys']:
                        part_keys.append(i['Name'])
                    parse_table_dict['partition_keys'] = part_keys
                    yield parse_table_dict
                else:
                    logger.warn("!! No partitions found for table {} !!".format(res["TableList"][i]['Name']))
            else:
                logger.warn("!! No partitions found for table {} !!".format(res["TableList"][i]['Name']))


        
    def batch_partition_input_list(self,s3_prefix_list,parse_table_dict):
        '''

        Creates a list of dictionaries of Values and StorageDescriptor for each Partition

        Parameters:
        s3_prefix_list = list of s3_prefixes for a particular table
        head_prefix = head prefix on the s3 prefix common for all the tables
        storage_desc = StorageDescriptor for the table instance

        Return:
        partition_input_list= list of dicts with 
        Values - list of values for the partition keys ex: [2020-01-01,01]
        StorageDescription - contains location element ex: s3:/bucket/location/datekey=2020-01-01/hour=01

        '''

        partition_input_list=[]
        custom_storage_descriptor = parse_table_dict['storage_desc']
        head_prefix = parse_table_dict['head_prefix']
        storage_bucket = parse_table_dict['bucket_name']
        if( len(s3_prefix_list)==0 ) :
            logger.info("s3_prefix_list is empty for table: {0}".format(parse_table_dict['table_name']))
        for i in s3_prefix_list:
            part_values_s3_prefix = []
            split_prefix = (i.replace(head_prefix,"").split("/"))
            for j in range(1,len(split_prefix)):
                if(split_prefix[j]!=""):
                    part_values_s3_prefix.append(split_prefix[j].split("=")[1])
            
            # Create custom storage descriptor for s3 location
            custom_storage_descriptor['Location'] = "s3://"+storage_bucket+"/"+i

            if(len(part_values_s3_prefix) == len(parse_table_dict['partition_keys'])):
                tempdict = {}
                tempdict['Values'] = part_values_s3_prefix
                tempdict['StorageDescriptor'] = custom_storage_descriptor
                # Use deepcopy as each StorageDescription dict needs to be a unique value for the partition
                partition_input_list.append(copy.deepcopy(tempdict))

        return partition_input_list

    def create_batch_partition_call(self,DatabaseName,TableName,partition_input_list):
        '''
        
        Runs a Glue Batch API call for creating partitions on one table at a time

        Parameters:
        DatabaseName = Name of the database
        TableName = Name of the table
        partition_input_list = generated from batch_partition_input_list method

        Return:
        create_partition_response = Returns response from the API on success and failure of batch partition call

        '''
        try:
            while True:
                str_len_input = str(len(partition_input_list))
                logger.info("length of partition input list {0}".format(str_len_input))
                if(len(partition_input_list) > 99):
                    partition_input_list_new = partition_input_list[0:99]
                    partition_input_list =  partition_input_list[99:]
                    create_partition_response = self.glue_client.batch_create_partition(
                                    DatabaseName=DatabaseName,
                                    TableName=TableName,
                                    PartitionInputList=partition_input_list_new
                    )
                else:
                    create_partition_response = self.glue_client.batch_create_partition(
                        DatabaseName=DatabaseName,
                        TableName=TableName,
                        PartitionInputList=partition_input_list
                    )
                    break

            return create_partition_response

        except ClientError as e:
            if e.response['Error']['Code'] == 'ExpiredTokenException':
                logger.error("Expired Token Given please check..")
                sys.exit()
            if e.response['Error']['Code'] == 'EntityNotFoundException':
                print(e)
                logger.error("Invalid Database Name Given: {}".format(DatabaseName))
                raise e
            if e.response['Error']['Code'] == 'InvalidInputException':
                logger.error("Invalid Input Given")
                raise e
            else:
                logger.error("Unknown Error Found: ", e)
                raise e
        except Exception as e:
            logger.error("Unknown Exception Found")
            raise e
