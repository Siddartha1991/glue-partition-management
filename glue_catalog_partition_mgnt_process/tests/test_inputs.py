s3_prefix_list = ['qtweets/message/PartitionEvent/fromapp=20122/datekey=2020-01-01/hour=03/','qtweets/message/PartitionEvent/fromapp=20122/datekey=2020-01-01/hour=04/']
head_prefix = "qtweets/message/"

parse_table_dict = {'table_prefix_name': 'PartitionEvent', 'bucket_name': 'ql-dl-raw-streaming-qtweets-801554245576-us-east-2-sandbox', 'head_prefix': 'qtweets/message/', 'storage_desc': {'Columns': [{'Name': 'id', 'Type': 'string'}], 'Location': 's3://ql-dl-raw-streaming-qtweets-801554245576-us-east-2-sandbox/qtweets/message/PartitionEvent/', 'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat', 'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat', 'Compressed': False, 'NumberOfBuckets': 0, 'SerdeInfo': {'SerializationLibrary': 'org.apache.hadoop.hive.serde2.OpenCSVSerde', 'Parameters': {'separatorChar': ','}}, 'SortColumns': [], 'StoredAsSubDirectories': False}, 'table_name': 'partitionevent', 'partition_keys': ['fromapp', 'datekey', 'hour']}

storage_desc = {'Columns': [
                    {'Name': 'id',
                    'Type': 'string'
                    }
                    ],
                    'Location': 's3://ql-dl-raw-streaming-qtweets-801554245576-us-east-2-sandbox/qtweets/message/PartitionEvent/',
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'Compressed': False,
                    'NumberOfBuckets': 0,
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.serde2.OpenCSVSerde',
                        'Parameters': {'separatorChar': ','}
                                },
                    'SortColumns': [],
                    'StoredAsSubDirectories': False
                    }

expected_partition_input_list = [{'Values': ['20122', '2020-01-01', '03'], 
                                    'StorageDescriptor': 
                                        {'Columns': [
                                            {'Name': 'id', 'Type': 'string'}
                                            ],
                                            'Location': 's3://ql-dl-raw-streaming-qtweets-801554245576-us-east-2-sandbox/qtweets/message/PartitionEvent/fromapp=20122/datekey=2020-01-01/hour=03/',
                                            'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                                            'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                                            'Compressed': False,
                                            'NumberOfBuckets': 0,
                                            'SerdeInfo': {
                                                'SerializationLibrary': 'org.apache.hadoop.hive.serde2.OpenCSVSerde',
                                                'Parameters': {'separatorChar': ','}
                                                        },
                                            'SortColumns': [],
                                            'StoredAsSubDirectories': False
                                            }
                                    }, 
                                {'Values': ['20122', '2020-01-01', '04'],
                                    'StorageDescriptor':
                                        {'Columns': [
                                            {'Name': 'id', 'Type': 'string'}
                                            ],
                                            'Location': 's3://ql-dl-raw-streaming-qtweets-801554245576-us-east-2-sandbox/qtweets/message/PartitionEvent/fromapp=20122/datekey=2020-01-01/hour=04/',
                                            'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                                            'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                                            'Compressed': False,
                                            'NumberOfBuckets': 0,
                                            'SerdeInfo': {
                                                'SerializationLibrary': 'org.apache.hadoop.hive.serde2.OpenCSVSerde',
                                                'Parameters': {
                                                    'separatorChar': ','
                                                    }
                                                },
                                                'SortColumns': [],
                                                'StoredAsSubDirectories': False
                                        }
                                    }
                                ]