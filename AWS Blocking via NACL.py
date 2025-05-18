import boto3
from netaddr import IPSet, IPNetwork
from botocore.exceptions import ClientError
import json

def read_and_condense_ips(file_path):
    """Read a .txt file of IP addresses and condense them into CIDR ranges."""
    with open(file_path, 'r') as f:
        ip_list = [line.strip() for line in f if line.strip()]

    ip_set = IPSet(ip_list)
    return [str(cidr) for cidr in ip_set.iter_cidrs()]

def update_nacl(client, vpc_id, subnet_ids, cidr_blocks, region):
    """Create or update a NACL in a specific VPC."""
    try:
        # Fetch existing NACLs
        nacls = client.describe_network_acls(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['NetworkAcls']

        # Create a new NACL if none exist in the VPC
        if not nacls:
            nacl = client.create_network_acl(VpcId=vpc_id)
            nacl_id = nacl['NetworkAcl']['NetworkAclId']
        else:
            nacl_id = nacls[0]['NetworkAclId']  # Use the first available NACL

        # Revoke existing deny rules
        entries = client.describe_network_acls(NetworkAclIds=[nacl_id])['NetworkAcls'][0]['Entries']
        for entry in entries:
            if not entry['Egress'] and 'RuleAction' in entry and entry['RuleAction'] == 'deny':
                client.delete_network_acl_entry(NetworkAclId=nacl_id, RuleNumber=entry['RuleNumber'], Egress=False)

        # Add deny rules for the new CIDR blocks
        rule_number = 100
        for cidr in cidr_blocks:
            client.create_network_acl_entry(
                NetworkAclId=nacl_id,
                RuleNumber=rule_number,
                Protocol="-1",
                RuleAction="deny",
                Egress=False,
                CidrBlock=cidr
            )
            rule_number += 1

        # Associate the NACL with all subnets
        for subnet_id in subnet_ids:
            client.associate_network_acl(NetworkAclId=nacl_id, SubnetId=subnet_id)

        print(f"NACL updated successfully in region {region} for VPC {vpc_id}")

    except ClientError as e:
        print(f"Failed to update NACL: {e}")


def propagate_to_accounts(ou_id, ip_file_path):
    """Propagate NACL changes to all accounts in an AWS OU."""
    org_client = boto3.client('organizations')
    sts_client = boto3.client('sts')

    # Get all accounts in the OU
    accounts = org_client.list_accounts_for_parent(ParentId=ou_id)['Accounts']

    for account in accounts:
        account_id = account['Id']
        role_arn = f"arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole"

        # Assume role for the account
        try:
            assumed_role = sts_client.assume_role(RoleArn=role_arn, RoleSessionName="NACLUploader")
            creds = assumed_role['Credentials']
            ec2_client = boto3.client('ec2',
                                      aws_access_key_id=creds['AccessKeyId'],
                                      aws_secret_access_key=creds['SecretAccessKey'],
                                      aws_session_token=creds['SessionToken'])

            regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

            for region in regions:
                regional_client = boto3.client('ec2', region_name=region,
                                               aws_access_key_id=creds['AccessKeyId'],
                                               aws_secret_access_key=creds['SecretAccessKey'],
                                               aws_session_token=creds['SessionToken'])

                vpcs = regional_client.describe_vpcs()['Vpcs']
                for vpc in vpcs:
                    vpc_id = vpc['VpcId']
                    subnets = regional_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
                    subnet_ids = [subnet['SubnetId'] for subnet in subnets['Subnets']]

                    cidr_blocks = read_and_condense_ips(ip_file_path)
                    update_nacl(regional_client, vpc_id, subnet_ids, cidr_blocks, region)

        except ClientError as e:
            print(f"Failed to assume role for account {account_id}: {e}")

if __name__ == "__main__":
    IP_FILE_PATH = "path/to/ip_list.txt"
    OU_ID = "your-ou-id"

    propagate_to_accounts(OU_ID, IP_FILE_PATH)
