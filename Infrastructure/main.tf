# Infrastructure as Code - AWS Cloud Lab
# Managed by Tuan Anh

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-southeast-1" # Singapore
}

resource "aws_instance" "sre_portfolio" {
  ami           = "ami-0df7a207adb894a1f" # Amazon Linux 2023
  instance_type = "t3.micro"
  key_name      = "cloud-lab-key"

  tags = {
    Name        = "SRE-Portfolio-Instance"
    Environment = "Dev"
    ManagedBy   = "Terraform"
  }

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y docker
              systemctl start docker
              systemctl enable docker
              EOF
}
