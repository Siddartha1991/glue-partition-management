from botocore.exceptions import ClientError
from modules.ProcessLogger import setup_logging
import boto3
import botocore
from collections import defaultdict
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import awswrangler as wr

logger = setup_logging().getLogger(__name__)

class S3PrefixGeneration:
    
    def __init__(self,s3_client):
        self.s3_client = s3_client
        #datelist
        self.datelist = ['datekey','dt','date','lastmodified','month','year','yr', 'day']
        self.date_formats = ["%Y-%m-%d", "%d-%m-%Y", "%Y.%m.%d", "%d.%m.%Y","%d%m%Y", "%Y%m%d"]
        self.month_formats = ["%Y.%m", "%Y-%m", "%Y%m", "%m"]
        self.year_formats = ["%Y"]
        self.day_formats = ["%d"]
        self.bucket_name = ""

    '''
        Creates a list of latest partitions that are retrieved from s3 for each table

        Parameters:
        parse_table_dict = Dictionary with all values that are needed for making call to s3 and get latest parameters

        Return:
        partitionlist= list of latest partitions 
        
    '''
    def get_s3partition_list(self, parse_table_dict):        
        try:
            partitionlist = []            
            #Build SourcePrefix from inputdict
            sourceprefix = parse_table_dict['head_prefix'] + parse_table_dict['table_prefix_name']  +'/'
            self.bucket_name = parse_table_dict['bucket_name'] 
            
            #creating a copy of partitions so it wont change initial object and call get partitions
            paritions = parse_table_dict['partition_keys'][:]
            self.getpartitions(sourceprefix, partitionlist, paritions)
            return partitionlist
        except Exception as e:
            logger.error("Unknown Error Found")
            raise e

    '''
        gets partitions by date for each table and appends to partitionlist if it finds any in last 2 days or last 3 hours depending on type of partition

        Parameters:
        sourceprefix = name of the prefix to retrieve latest partitions from s3
        partitionlist = list to append latest partition values to
        partitions = partitionkeys used to create prefix and retrieve partitions
        
    '''
    def getprefixesbytimepartitiontype(self,sourceprefix, partitionlist, partitions):
        try:
            partitionprefixes = []
            values_to_check = []
            #get format  (month year, year, month)
            formatlst = self.getfirstprefixgeneratedateformat(sourceprefix)
            self.generatecurrentpreviousvalues(values_to_check, formatlst)
            if len(values_to_check) > 0:
                for value in values_to_check:
                    sourcetimeprefix = sourceprefix + partitions[0] + '=' + value + '/'
                    if partitions[0] in ['monthyear','year','month']:
                        prefixess = self.getprefixesbypartitiontype(sourcetimeprefix)
                        if prefixess.get('KeyCount') >= 1:
                            partitionprefixes.append(sourcetimeprefix)
                    else:
                        prefixess = self.getprefixesbypartitiontype(sourcetimeprefix)
                        if prefixess.get('CommonPrefixes') is not None:
                            for prefix in prefixess.get('CommonPrefixes'):
                                partitionprefixes.append(prefix['Prefix'])
                        elif prefixess.get('CommonPrefixes') is None and prefixess.get('KeyCount') >= 1:
                            partitionlist.append(sourcetimeprefix)
            else:
                logger.error("Unique format not found for SourcePrefix : " + sourceprefix)
                
            partitions.pop(0)
            return partitionprefixes
        except Exception as e:
            logger.error("Unknown Error Found")
            raise e

    '''
        searches for latest partitions by looping through each folder and subfolders and returns a list of partitions

        Parameters:
        sourceprefix = name of the prefix to retrieve latest partitions from s3
        partitionlist = list to append latest partition values to
        partitions = partitionkeys used to create prefix and retrieve partitions
        
    '''
    def getpartitions(self,sourceprefix, partitionlist, partitions):
        try:
            if(len(partitions) > 0):
                if(any(datelst in partitions[0] for datelst in self.datelist)):
                    dateprefixes = self.getprefixesbytimepartitiontype(sourceprefix, partitionlist, partitions)
                    if dateprefixes is not None:
                        for dateprefix in dateprefixes:
                            partitionscopy = partitions[:]
                            self.getpartitions(dateprefix, partitionlist, partitionscopy)
                elif(partitions[0].find('header') != -1):
                    self.getattunitypartitions(sourceprefix, partitions, partitionlist)
                else:
                    partitionprefixes = self.getprefixesbypartitiontype(sourceprefix)
                    partitions.pop(0)
                    if partitionprefixes.get('CommonPrefixes') is not None:
                        for partitionprefix in partitionprefixes.get('CommonPrefixes'):
                            partitionscopy = partitions[:]
                            self.getpartitions(partitionprefix['Prefix'], partitionlist, partitionscopy)
                    else:
                        partitionlist.append(sourceprefix)
            else:
                partitionlist.append(sourceprefix)
        except Exception as e:
            logger.error("Unknown Error Found")
            raise e
    
    '''
        gets prefixes for any sourceprefix with delimiter

        Parameters:
        sourceprefix = name of the prefix to retrieve latest partitions from s3
        
    '''
    def getprefixesbypartitiontype(self,sourceprefix):
        try:            
            sources = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix= sourceprefix,
                    Delimiter='/'
                    )
            return sources
        except Exception as e:
            logger.error("Unknown Error Found")
            raise e

    '''
        gets partitions for attunity partition in last 2 days or last 3 hours depending on type of partition as these are partitioned different than other products

        Parameters:
        sourceprefix = name of the prefix to retrieve latest partitions from s3
        partitionlist = list to append latest partition values to
        partitions = partitionkeys used to create prefix and retrieve partitions
        
    '''
    def getattunitypartitions(self,sourceprefix, partitions, partitionlist):
        try:            
            values_to_check = []

            sources = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix= sourceprefix,
                    MaxKeys=100,
                    Delimiter='/'
                    )

            if sources.get('CommonPrefixes') is not None:
                for source in sources.get('CommonPrefixes'):
                    if 'header' in source['Prefix']:
                        headerKeyPrefix = source['Prefix']
                        break

                if headerKeyPrefix is not None:

                    keyprefix = headerKeyPrefix.split('/')[-2].split('=')[-1].split('_') 
                    self.generatecurrentpreviousvaluesforattunity(values_to_check, keyprefix)
                    
                    for value in values_to_check:
                        sourcetimeprefix = sourceprefix + partitions[0] + '=' + value
                        #Using AWSWrangler to get directories based on value that's passed in This function takes wildcards to generate directories and is fast than aws cli ls and python filter
                        filteredprefixes = wr.s3.list_directories('s3://'+ self.bucket_name + '/' + sourcetimeprefix)

                        if len(filteredprefixes) > 0:
                            for filteredprefix in filteredprefixes:
                                partitionval = '/'.join(filteredprefix.split('/')[3:-1])
                                partitionlist.append(partitionval)


                    partitions.pop(0)          
                    
        except Exception as e:
            logger.error("Unknown Error Found")
            raise e

    '''
        gets top record for sourceprefix and split the value to get date and type and pass to getformat function to get date format

        Parameters:
        sourceprefix = name of the prefix to retrieve latest partitions from s3
        
    '''
    def getfirstprefixgeneratedateformat(self,sourceprefix):
        match = []
        try:            
            #make s3 call
            sources = self.s3_client.list_objects_v2(
                        Bucket=self.bucket_name,
                        Prefix= sourceprefix,
                        MaxKeys=5,
                        Delimiter='/'
                        )
            if sources.get('CommonPrefixes') is not None:
                keyprefix = sources.get('CommonPrefixes')[0]['Prefix'].split('/')[-2] 
                datekeyprefix = keyprefix.split('=')[-1]
                typeprefix = keyprefix.split('=')[0]
                self.getformat(datekeyprefix,typeprefix,match)
        except Exception as e:
            logger.error("Unknown Error Found",e)
            raise e

        return match
    
    '''
        Takes datekey as input and searches through all datetime format arrays and returns a format that matched the date

        Parameters:
        datekeyprefix = date/month/day to get format
        typeprefix = type of prefix - This is being used to remove confusion if value is month/day as both can be viceversa when deriving formats
        match = list to append format matches to
        
    '''
    def getformat(self,datekeyprefix,typeprefix,match):
        formats = [self.date_formats, self.month_formats, self.year_formats, self.day_formats]
        for fmtlst in formats:
            for fmt in fmtlst:
                try:
                    datetime.strptime(datekeyprefix, fmt)
                    if len(datekeyprefix) >= 4 and len(datekeyprefix) <= 6 and fmt not in self.date_formats:
                        match.append(fmt)
                    elif len(datekeyprefix) == 2 and typeprefix == 'month' and fmt in self.month_formats:
                        match.append(fmt)
                    elif len(datekeyprefix) == 2 and typeprefix in ['day','date'] and fmt in self.day_formats:
                        match.append(fmt)
                    elif len(datekeyprefix) > 6:
                        match.append(fmt)
                except ValueError as e:
                    continue        

    '''
        Takes Sourceprefix and generates a format for date and returns list of values to check to get latest partitions

        Parameters:
        values_to_check = List to add current and previous values to 
        formatlst = date, monthm day format to generate values
                
    '''
    def generatecurrentpreviousvalues(self, values_to_check, formatlst):
        try:            
            if len(formatlst) == 1:
                format = formatlst[0]
                if format in self.date_formats:
                    values_to_check.append(datetime.strftime(datetime.now(), format))
                    values_to_check.append(datetime.strftime(datetime.now() - timedelta(1), format))
                elif format in self.month_formats:
                    values_to_check.append(datetime.strftime(datetime.now(), format))
                    values_to_check.append(datetime.strftime(datetime.now() + relativedelta(months=-1), format))
                elif format in self.year_formats:
                    values_to_check.append(datetime.strftime(datetime.now(), format))
                    values_to_check.append(datetime.strftime(datetime.now() + relativedelta(years=-1), format))
                elif format in self.day_formats:
                    values_to_check.append(datetime.strftime(datetime.now(), format))
                    values_to_check.append(datetime.strftime(datetime.now() + relativedelta(days=-1), format))
            else:
                logger.error("Unique format not found")
                        
        except Exception as e:
            logger.error("Unknown Error Found")
            raise e

    '''
        Takes attunity keyprefix breaks the date and time and generates a format for date and returns list of values to check to get latest partitions

        Parameters:
        values_to_check = List to add current and previous values to 
        formatlst = date, monthm day format to generate values
                
    '''
    def generatecurrentpreviousvaluesforattunity(self, values_to_check, keyprefix):
        try:
            formatmatch = []

            datekeyprefix = keyprefix[0].split('T')[0]
            timekeyprefix = keyprefix[0].split('T')[-1]
            timekeyprefix2 = keyprefix[1].split('T')[-1]
            #Calls get format method and passes dateprefix to get dateformat
            self.getformat(datekeyprefix,'', formatmatch)
            # Building values to get partitions for -  In AttunityCase If time is 00000 getting partitions from last 2 days. If time is not 00000 then getting partitions from last 3 hours on same day
            if len(formatmatch) == 1:
                dateformat = formatmatch[0]
                if(timekeyprefix == '000000' and timekeyprefix2 == '000000'):
                    values_to_check.append(datetime.strftime(datetime.now(), dateformat))
                    values_to_check.append(datetime.strftime(datetime.now() - timedelta(1), dateformat))
                else:
                    values_to_check.append(datetime.strftime(datetime.now(), dateformat+'T%H'))
                    values_to_check.append(datetime.strftime(datetime.now() - timedelta(hours=1), dateformat+'T%H'))
                    values_to_check.append(datetime.strftime(datetime.now() - timedelta(hours=2), dateformat+'T%H'))
            else:
                logger.error("Unique format not found for keyprefix1 : {0} - Keyprefix2 : {1} ".format(keyprefix[0], keyprefix[1]))
        except Exception as e:
            logger.error("Unknown Error Found")
            raise e
    
