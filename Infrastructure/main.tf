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

# ------------------------------------------------------------------------------
# PROVIDER CONFIGURATION
# ------------------------------------------------------------------------------
# Target Region: Singapore (Optimized for lowest latency to VN/SEA users)
provider "aws" {
  region = "ap-southeast-1" 
}

# ------------------------------------------------------------------------------
# SECURITY GROUP: Inbound/Outbound Traffic Control
# ------------------------------------------------------------------------------
# Applying Principle of Least Privilege (PoLP) for exposed ports.
resource "aws_security_group" "lab_sg" {
  name        = "cloud_lab_sg"
  description = "Security Group for SRE Portfolio - Microservices & SSH access"

  # Admin Access (SSH)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Note: In production, restrict to corporate VPN IP
  }

  # Microservices Exposed Ports (NetProbe, FaceAuth, SOS)
  ingress {
    from_port   = 8081
    to_port     = 8083
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound Rules (Allow instance to fetch Docker images and updates)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ------------------------------------------------------------------------------
# COMPUTE INSTANCE: Amazon Linux 2023 
# ------------------------------------------------------------------------------
resource "aws_instance" "sre_portfolio" {
  ami           = "ami-0df7a207adb894a1f" # AL2023 standard AMI
  instance_type = "t3.micro"              # FinOps: Free-tier eligible compute
  key_name      = "cloud-lab-key"
  
  # Attach the Security Group defined above
  vpc_security_group_ids = [aws_security_group.lab_sg.id]

  # Metadata tagging for cost allocation and resource tracking
  tags = {
    Name        = "SRE-Portfolio-Instance"
    Environment = "Dev"
    ManagedBy   = "Terraform"
    Project     = "Cloud-Lab"
  }

  # ----------------------------------------------------------------------------
  # BOOTSTRAPPING (User Data)
  # Automatically install and enable Docker daemon upon instance initialization.
  # ----------------------------------------------------------------------------
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y docker
              systemctl start docker
              systemctl enable docker
              EOF
}
