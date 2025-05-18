resource "aws_s3_bucket" "secure_bucket" {
	bucket = var.bucket_name

	tags = {
		Name = "Secure S3 Bucket"
	}
}

resource "aws_s3_bucket_versioning" "versioning" {
	bucket = aws_s3_bucket.secure_bucket.id

	versioning_configuration {
		status = "Enabled"
	}
}

resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {
	bucket = aws_s3_bucket.secure_bucket.id

	rule {
		apply_server_side_encryption_by_default {
			sse_algorithm = "AES256"
		}
	}
}

resource "aws_s3_bucket_public_access_block" "block" {
	bucket                  = aws_s3_bucket.secure_bucket.id
	block_public_acls       = false
	block_public_policy     = false
	ignore_public_acls      = false
	restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "allow_specific_ip" {
	bucket = aws_s3_bucket.secure_bucket.id

	policy = jsonencode({
		Version = "2012-10-17"
		Statement = [
			{
				Sid       = "IPAllow"
				Effect    = "Allow"
				Principal = "*"
				Action    = "s3:GetObject"
				Resource  = "${aws_s3_bucket.secure_bucket.arn}/*"
				Condition = {
					IpAddress = {
						"aws:SourceIp" = var.allowed_cidr
					}
				}
			}
		]
	})
}
