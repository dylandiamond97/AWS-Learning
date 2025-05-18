variable "aws_region" {
	description = "AWS region"
	type        = string
	default     = "us-east-1"
}

variable "aws_profile" {
	description = "AWS CLI profile name"
	type        = string
	default     = "default"
}

variable "bucket_name" {
	description = "Name of the S3 bucket"
	type        = string
}

variable "allowed_cidr" {
	description = "CIDR block allowed to access the bucket"
	type        = string
}
