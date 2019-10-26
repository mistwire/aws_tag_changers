###############################################################################
# Patch Group modification (automated process)
# This program prompts the user to input a csv file.
# Once is has this info it will modify the Patch Group tags that it id's per row
# Created: 2019.09.02 by Chris F. Williams
# Updated: 
###############################################################################
# To Do List:
# 1. add logging output - DONE
# 2. log to CloudWatch - DONE
# 3. email notification - 
# 4. add Name to instanceID output - DONE
###############################################################################

import boto3
from csv import DictReader
import watchtower
import logging

# Setup local logging & level:
logging.basicConfig(filename='autoPGchanger.log',level=logging.INFO,format='%(asctime)s %(message)s')

# Setup CloudWatch logging configuration using watchtower module:
cwlogger = logging.getLogger(__name__)
cwlogger.addHandler(watchtower.CloudWatchLogHandler())


# Create variable for the csv file from input:
csv_file = input("Please type in the full path to the csv file you want to import: \n")

# get the csv file & set variables: 
with open(csv_file, encoding='utf-8-sig') as file:
    csv_reader = DictReader(file)
    for row in csv_reader:
        # establish region:
        rgn = row['Region']
        # establish Patch Group value:
        patch_group = row['Patch Group']
        # get filters as a list of dictionaries:
        filters = [
            dict(Name= 'tag:' + csv_reader.fieldnames[1], Values= [row['CustomerName']]),
            dict(Name= 'tag:' + csv_reader.fieldnames[2], Values= [row['AvailabilityZone']]),
            dict(Name= 'tag:' + csv_reader.fieldnames[3], Values= [row['Env']]), 
        ]    
        # instantiate ec2 variable:
        ec2client = boto3.client('ec2', region_name=rgn) 
        # get response based on filters from filters list:
        response = ec2client.describe_instances(Filters=filters) 
        instancelist = []
        namelist = []
        for reservation in (response["Reservations"]):
            for instance in reservation["Instances"]:
                instancelist.append(instance["InstanceId"])
                for tags in instance["Tags"]:
                    if tags["Key"] == 'Name':
                        namelist.append(tags["Value"])
        print(f"Changing {namelist} to {patch_group}")
        logging.info(f"Changing value of Patch Group tag to {patch_group} for the following systems: {namelist}") # log locally
        cwlogger.info(f"Changing value of Patch Group tag to {patch_group} for the following systems: {namelist}") # log to CloudWatch

        ec2 = boto3.client('ec2', region_name=rgn)
        ec2.create_tags(
            Resources=instancelist,
            Tags=[
                {
                    'Key': 'Patch Group',
                    'Value': patch_group
                }
            ]
        )
