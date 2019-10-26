###############################################################################
# Patch Group modification (manual process)
# This program prompts the user to input region, new Patch Group name, and filtering tags/values
# Once is has this info it will modify the Patch Group tags that it id's in the specified region
# Created: 2019.08.22 by Chris F. Williams
# Updated: 
###############################################################################
# To Do List:
# 1. add multiple tag filtering option - DONE
# 2. add InstanceID validation - DONE
# 3. add logging output - DONE
# 4. email notification
# 5. add Name to instanceID output - DONE
# 6. 
###############################################################################

import boto3
import watchtower
import logging

# setup local logging & level:
logging.basicConfig(filename='manPGchanger.log',level=logging.INFO,format='%(asctime)s %(message)s')

# Setup CloudWatch logging configuration using watchtower module:
cwlogger = logging.getLogger(__name__)
cwlogger.addHandler(watchtower.CloudWatchLogHandler())

# Establish region
rgn = input("[REGION] What region are the EC2 instances that you want to modify(us-west-1, eu-west-1, ap-southeast-2)?: \n").lower()

# Get name of Patch Group that you want to apply to said EC2 instances
patch_group = input("[PATCH GROUP] What is the value for Patch Group that you want to apply?: \n")


# Get a list of filters from console
filters = []
while True:
    tagkey = input("[FILTER] What tag key are you using? (hit enter <blank line> to quit): \n")
    if (tagkey):
        tagvalue = input("[FILTER] What tag value are you filtering on?: \n")
        filter = dict(Name= 'tag:' + tagkey, Values= [tagvalue])
        # print(filter)
        filters.append(filter) # append to filter list as dictionary
    else:
        break # do until input is blank

# print(filters)

# Apply filters and get back a list of relevant ec2 instances:
ec2client = boto3.client('ec2', region_name=rgn)
response = ec2client.describe_instances(Filters=filters)
instancelist = []
namelist = []

for reservation in (response["Reservations"]):
    for instance in reservation["Instances"]:
        instancelist.append(instance["InstanceId"])
        for tags in instance["Tags"]:
            if tags["Key"] == 'Name':
                namelist.append(tags["Value"])

zipped = zip(namelist, instancelist)
[print(i) for i in zipped]

proceed = input(f"Do you want to change Patch Group tag to {patch_group} for the above EC2 Instances? (y/n) \n")
if proceed.lower() == 'y':
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
    # send to logs:
    logging.info(f"Changing value of Patch Group tag to {patch_group} for the following systems: {namelist}") # log locally
    cwlogger.info(f"Changing value of Patch Group tag to {patch_group} for the following systems: {namelist}") # log to CloudWatch
