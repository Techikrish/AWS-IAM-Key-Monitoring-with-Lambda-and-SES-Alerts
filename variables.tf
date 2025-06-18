variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "sender_email" {
  description = "SES-verified sender email address"
  type        = string
}

variable "recipient_email" {
  description = "Recipient email address for alerts"
  type        = string
}

variable "max_key_age" {
  description = "Maximum age of IAM keys in days"
  type        = number
  default     = 90
}

variable "max_unused_days" {
  description = "Maximum unused period of IAM keys in days"
  type        = number
  default     = 30
}