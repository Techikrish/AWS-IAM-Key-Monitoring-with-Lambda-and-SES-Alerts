## Project Overview

This project automates IAM access key monitoring to enhance AWS account security. The Lambda function, written in Python, uses `boto3` to check IAM keys and sends email alerts via SES when issues are detected. Terraform deploys the Lambda, IAM role, and EventBridge schedule for daily execution. Alerts are sent to a configured email address, ensuring timely action to rotate or deactivate problematic keys.

## Features

- **Monitors IAM Access Keys** for:
    - Keys older than 90 days (configurable).
    - Keys unused for 30 days (configurable).
    - Inactive keys.
    - Keys created but never used.
- **Automated Email Alerts** via AWS SES with detailed reports.
- **Infrastructure-as-Code** using Terraform for Lambda, IAM role, and EventBridge.
- **Daily Scheduling** via AWS EventBridge.
- **Error Handling** with SES notifications for Lambda failures.
- **Secure Configuration** using environment variables for email addresses.

## Prerequisites

- **AWS Account** with an IAM user having admin access (`AdministratorAccess` policy).
- **Terraform** installed (version 1.5+ recommended).
- **AWS CLI** (optional, for testing SES or IAM).
- **Email Addresses**:
    - Sender email (e.g., `alerts@yourcompany.com`) for SES alerts.
    - Recipient email (e.g., `security@yourcompany.com`) to receive alerts.
- **AWS Region**: `us-east-1` (configurable in `terraform.tfvars`).

## Project Structure

```
iam-key-monitor/
├── lambda_function.py      # Python code for the Lambda function
├── main.tf                 # Terraform configuration for Lambda, IAM, EventBridge
├── variables.tf            # Terraform input variables
├── outputs.tf              # Terraform outputs
├── terraform.tfvars        # Terraform variable values (gitignored)
└── README.md               # Project documentation
```

- **`lambda_function.py`**: Monitors IAM keys and sends SES alerts.
- **`main.tf`**: Defines AWS resources (Lambda, IAM role, EventBridge).
- **`terraform.tfvars`**: Configures sender/recipient emails and thresholds.

## Setup Instructions

### Configure AWS SES

1. **Access SES Console**:
    - Log in to the AWS Console and navigate to **SES** in `us-east-1`.
2. **Verify Sender Email**:
    - Go to **Verified Identities** > **Create Identity** > **Email Address**.
    - Enter `alerts@yourcompany.com` and click **Create Identity**.
    - Check the email’s inbox for a verification link and click it.
    - Confirm status is **Verified**.
3. **Verify Recipient Email (if in Sandbox Mode)**:
    - Check **SES** > **Account Dashboard** for sandbox status.
    - If in sandbox, verify `security@yourcompany.com` similarly.
4. **Optional: Move Out of Sandbox**:
    - Go to **Edit Sending Limits** > **Request Production Access**.
    - Submit a support case to send to unverified recipients.
5. **Test SES**:
    - Use **Send Test Email** in SES to confirm emails are sent from `alerts@yourcompany.com` to `security@yourcompany.com`.

### Set Up Terraform

1. **Install Terraform**:
    - Download and install Terraform from [terraform.io](https://www.terraform.io/downloads.html).
2. **Clone or Create Repository**:
    - Clone this repository:
        
        ```bash
        git clone https://github.com/Techikrish/AWS-IAM-Key-Monitoring-with-Lambda-and-SES-Alerts.git
        cd iam-key-monitor
        ```
        
    - Or create a new repository and copy the provided files.
3. **Configure AWS Credentials**:
    - Set up AWS CLI with your IAM user’s credentials:
        
        ```bash
        aws configure
        ```
        
        - Enter your access key, secret key, and region (`us-east-1`).
    - Or use environment variables:
        
        ```bash
        export AWS_ACCESS_KEY_ID=your_access_key
        export AWS_SECRET_ACCESS_KEY=your_secret_key
        export AWS_DEFAULT_REGION=us-east-1
        ```
        
4. **Create `terraform.tfvars`**:
    - Copy `terraform.tfvars.example` (if provided) or create `terraform.tfvars`:
        
        ```
        aws_region       = "us-east-1"
        sender_email     = "alerts@yourcompany.com"
        recipient_email  = "security@yourcompany.com"
        max_key_age      = 90
        max_unused_days  = 30
        ```
        
    - Replace `sender_email` and `recipient_email` with your SES-verified emails.
    - Add `terraform.tfvars`

### Deploy with Terraform

1. **Initialize Terraform**:
    
    ```bash
    terraform init
    ```
    
2. **Review Plan**:
    
    ```bash
    terraform plan
    ```
    
3. **Deploy Resources**:
    
    ```bash
    terraform apply
    ```
    
    - Type `yes` to confirm.
    - This creates:
        - Lambda function (`IAMKeyMonitor`).
        - IAM role with SES and IAM permissions.
        - EventBridge rule for daily execution.

## Testing the Lambda Function

1. **Create a Test IAM Key**:
    - Go to **IAM** > **Users** > **Add Users**.
    - Create `test-key-user` with **Programmatic access**.
    - Download the access key CSV.
    - This triggers the “Keys Created but Never Used” alert.
2. **Run Lambda Manually**:
    - In the Lambda Console, go to **IAMKeyMonitor** > **Test**.
    - Create a test event:
        - Event Name: `TestIAMKeyMonitor`
        - JSON: `{}`
    - Click **Test** and check **Execution Results**.
    
    ![alert issue.PNG](alert_issue.png)
    
3. **Check Email Alert**:
    - Open `security@yourcompany.com`’s inbox.
    - Look for an email from `alerts@yourcompany.com` with subject “IAM Access Key Monitoring Alert”.
    - Example content:
        
        ```
        IAM Access Key Monitoring Report:
        
        Keys Created but Never Used:
        User: test-key-user, Key ID: AKIA..., Age: 0 days
        ```
        
    
    ![got-mail.PNG](got-mail.png)
    
4. **Test Other Conditions**:
    - **Old Keys**: Set `max_key_age=0` in `terraform.tfvars`, run `terraform apply`, and retest.
    - **Inactive Keys**: Deactivate the key in **IAM** > `test-key-user` > **Security Credentials**.
    - **Unused Keys**: Use the key (e.g., `aws s3 ls`), set `max_unused_days=0`, and reapply.
5. **Check Logs**:
    - Go to **CloudWatch** > **Log Groups** > `/aws/lambda/IAMKeyMonitor` for execution details.

## Troubleshooting

- **No Email Received**:
    - Verify `alerts@yourcompany.com` and `security@yourcompany.com` in **SES** > **Verified Identities**.
    - Check **SES** > **Sending Statistics** for rejections.
    - Ensure `terraform.tfvars` emails match SES-verified emails.
    - Check spam/junk folder.
- **Lambda Errors**:
    - Review CloudWatch Logs for SES or IAM issues.
    - Confirm Lambda IAM role has `ses:SendEmail` and IAM permissions.
- **No Alerts for Keys**:
    - Verify test key exists in **IAM** > **Users** > `test-key-user`.
    - Set `max_key_age=0` temporarily to force alerts.
- **Terraform Apply Fails**:
    - Check AWS credentials and region.
    - Review error messages for syntax or permission issues.

## 

---