import boto3
import os
from datetime import datetime, timezone
import json

# Environment variables
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'sender@example.com')
RECIPIENT_EMAIL = os.environ.get('RECIPIENT_EMAIL', 'admin@example.com')
MAX_KEY_AGE = int(os.environ.get('MAX_KEY_AGE', 90))  # Days
MAX_UNUSED_DAYS = int(os.environ.get('MAX_UNUSED_DAYS', 30))  # Days

# Initialize boto3 clients
iam_client = boto3.client('iam')
ses_client = boto3.client('ses')

def lambda_handler(event, context):
    """
    Monitor IAM access keys and send email alerts for:
    - Keys older than MAX_KEY_AGE days
    - Keys unused for MAX_UNUSED_DAYS days
    - Inactive keys
    - Keys created but never used
    """
    try:
        # List all IAM users
        users = iam_client.list_users()['Users']
        alerts = {
            'old_keys': [],
            'unused_keys': [],
            'inactive_keys': [],
            'never_used_keys': []
        }

        # Iterate through each user
        for user in users:
            username = user['UserName']
            # Get access keys for the user
            access_keys = iam_client.list_access_keys(UserName=username)['AccessKeyMetadata']
            
            for key in access_keys:
                key_id = key['AccessKeyId']
                create_date = key['CreateDate']
                status = key['Status']
                
                # Calculate key age
                key_age = (datetime.now(timezone.utc) - create_date).days
                
                # Get last used info
                last_used_info = iam_client.get_access_key_last_used(AccessKeyId=key_id)
                last_used_date = last_used_info['AccessKeyLastUsed'].get('LastUsedDate')
                
                # Common key info
                key_info = {
                    'UserName': username,
                    'AccessKeyId': key_id,
                    'AgeDays': key_age,
                    'LastUsed': str(last_used_date) if last_used_date else 'Never'
                }
                
                # Check for old keys (active keys older than MAX_KEY_AGE)
                if status == 'Active' and key_age > MAX_KEY_AGE:
                    alerts['old_keys'].append(key_info)
                
                # Check for unused keys (active keys not used for MAX_UNUSED_DAYS)
                if status == 'Active' and last_used_date:
                    days_unused = (datetime.now(timezone.utc) - last_used_date).days
                    if days_unused > MAX_UNUSED_DAYS:
                        key_info['DaysUnused'] = days_unused
                        alerts['unused_keys'].append(key_info)
                
                # Check for inactive keys
                if status == 'Inactive':
                    alerts['inactive_keys'].append(key_info)
                
                # Check for keys never used
                if status == 'Active' and not last_used_date:
                    alerts['never_used_keys'].append(key_info)

        # Prepare email if any alerts exist
        if any(alerts.values()):
            subject = "IAM Access Key Monitoring Alert"
            body = "IAM Access Key Monitoring Report:\n\n"
            
            # Old keys section
            if alerts['old_keys']:
                body += f"Keys Older Than {MAX_KEY_AGE} Days:\n"
               
                for key in alerts['old_keys']:
                    body += f"User: {key['UserName']}, Key ID: {key['AccessKeyId']}, Age: {key['AgeDays']} days, Last Used: {key['LastUsed']}\n"
                body += "\n"
            
            # Unused keys section
            if alerts['unused_keys']:
                body += f"Keys Unused for {MAX_UNUSED_DAYS} Days:\n"
                for key in alerts['unused_keys']:
                    body += f"User: {key['UserName']}, Key ID: {key['AccessKeyId']}, Unused: {key['DaysUnused']} days, Last Used: {key['LastUsed']}\n"
                body += "\n"
            
            # Inactive keys section
            if alerts['inactive_keys']:
                body += "Inactive Keys:\n"
                for key in alerts['inactive_keys']:
                    body += f"User: {key['UserName']}, Key ID: {key['AccessKeyId']}, Age: {key['AgeDays']} days, Last Used: {key['LastUsed']}\n"
                body += "\n"
            
            # Never used keys section
            if alerts['never_used_keys']:
                body += "Keys Created but Never Used:\n"
                for key in alerts['never_used_keys']:
                    body += f"User: {key['UserName']}, Key ID: {key['AccessKeyId']}, Age: {key['AgeDays']} days\n"
                body += "\n"
            
            # Send email via SES
            ses_client.send_email(
                Source=SENDER_EMAIL,
                Destination={'ToAddresses': [RECIPIENT_EMAIL]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': body}}
                }
                )
            return {
                'statusCode': 200,
                'body': json.dumps(f"Alert email sent for {sum(len(v) for v in alerts.values())} issues.")
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps("No IAM access key issues found.")
            }

    except Exception as e:
        error_message = f"Error in Lambda execution: {str(e)}"
        # Send error notification
        ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [RECIPIENT_EMAIL]},
            Message={
                'Subject': {'Data': "Error: IAM Key Monitoring Lambda Failed"},
                'Body': {'Text': {'Data': error_message}}
            }
        )
        return {
            'statusCode': 500,
            'body': json.dumps(error_message)
        }