def getname(instanceid,region):
    clientec2 = boto3.client(
        'ec2',
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        region_name=region,
    )
    response = clientec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-id',
                'Values': [instanceid,
                           ]
            },
        ],
    )
    for reservation in response['Reservations']:
        for instance in reservation["Instances"]:
            for tags in instance["Tags"]:
                if tags["Key"] == 'Name':
                    instancename = tags["Value"]
                else:
                    instancename = 'Unknown'
    return instancename

