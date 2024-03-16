import boto3

def lambda_handler(event, context):
    
    ec2 = boto3.setup_default_session(region_name='ap-south-1')
    ec2 = boto3.client('ec2')
    
    # Get all EBS snapshots
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']
    
    # Get all active EC2 instance and volume IDs
    instances = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running','terminated']}])['Reservations']
    active_instance_volume_ids = set()
    
    # Get active instance and volume IDs
    for reservation in instances:
        for instance in reservation['Instances']:
            for volume in instance['BlockDeviceMappings']:
                active_instance_volume_ids.add(volume['Ebs']['VolumeId'])
    
    # Iterate through snapshots and delete if not attached to any active instance or volume
    deleted_snapshots_count = 0
    for snapshot in snapshots:
        snapshot_id = snapshot['SnapshotId']
        volume_id = snapshot.get('VolumeId')
        
        if not volume_id or volume_id not in active_instance_volume_ids:
            # Delete the snapshot if it's not attached to any active instance or volume
            ec2.delete_snapshot(SnapshotId=snapshot_id)
            print(f"Deleted EBS snapshot {snapshot_id} as it was not attached to any active instance or volume.")
            deleted_snapshots_count += 1
    return {
    'statusCode': 200,
    'body': f'Deleted {deleted_snapshots_count} unused EBS snapshots.'
   }
            
