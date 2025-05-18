terraform {
  backend "s3" {
    bucket         = "ddiamo-terraform-state-dev"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "dev-tf-lock"
    encrypt        = true
  }
}
