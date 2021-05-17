import json
import boto3
import os
import logging
lambda_client = boto3.client('lambda')
glue_client = boto3.client('glue')
logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s %(funcName)s', level=logging.INFO,force=True)

def lambda_handler(event, context):
    logging.info("Parent Lambda Triggered")
    # get list of databases from glue
    res = glue_client.get_databases()
    db_list = res['DatabaseList']

    for i in db_list:
        db_name = i['Name']
        logging.info("db name being iterated {}".format(db_name))
        # filter raw databases only
        if ( db_name.endswith('_raw') and db_name != "amp_raw" and db_name != "lola_raw" ):            
            # get list of tables from input database
            tableslist = list_tables_for_db(db_name)
            for tables in tableslist:
                input_params = {'tables': tables, 'database_name': db_name}          
                logging.info("child lambda invoked for input_params being iterated:  {}".format(input_params))
                response = lambda_client.invoke(
                FunctionName= os.environ['PROCESS_LAMBDA'],
                InvocationType='Event', # async invocation
                Payload=json.dumps(input_params, default=str)
                )
        
    return "Parent Lambda Ran Successfully.."

def list_tables_for_db(database):
    '''
    Gets list of tables in a database provided using Glue API call
    '''
    try:
        next_token = ""
        response_list = []
        logging.info("fetching list of tables for db {}".format(database))
        while True:
            response = glue_client.get_tables(
                DatabaseName=database,
                NextToken=next_token
            )
            logging.info("num of tables found for database {0}: {1}".format(database,str(len(response["TableList"]))))
            response_list.append(response)
            next_token = response.get('NextToken')
            if (next_token is None):
                break
        return response_list
    except ClientError as e:
        if e.response['Error']['Code'] == 'ExpiredTokenException':
            print("***Expired Token Given please check..***")
            raise e
        if e.response['Error']['Code'] == 'EntityNotFoundException':
            print("***Invalid Database Name Given: {}***".format(database))
            raise e
        if e.response['Error']['Code'] == 'InvalidInputException':
            print("***Invalid Input Given:***")
            raise e
        else:
            print("***Unknown Error Found: ***", e)
            raise e
    except Exception as e:
        print("***Unknown Exception Found***")
        raise e


