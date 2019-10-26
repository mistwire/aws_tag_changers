import boto3
from csv import DictReader


bucket = "test-csv-pull"
file_name = "csvloggingtest.csv"

s3 = boto3.client('s3') 
# 's3' is a key word. create connection to S3 using default config and all buckets within S3

obj = s3.get_object(Bucket= bucket, Key= file_name) 
# get object and file (key) from bucket

for i in obj['Body']:
    print(i)