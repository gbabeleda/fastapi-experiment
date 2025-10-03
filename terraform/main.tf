terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Tell Terraform to use AWS
provider "aws" {
  region  = var.aws_region
  profile = "dev-admin"
}

# Upload SSH Key
resource "aws_key_pair" "deployer" {
  key_name   = "${var.project_name}-key"
  public_key = file(var.ssh_key_path)
}

# Get the default VPC
data "aws_vpc" "default" {
  default = true
}


# Create firewall rules
resource "aws_security_group" "app_server" {
  vpc_id      = data.aws_vpc.default.id
  name        = "${var.project_name}-sg"
  description = "Security group for ${var.project_name}"

  # Rule: Allow SSH (port 22) from anywhere
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # 0.0.0.0/0 means "the entire internet"
  }

  # Rule: Allow web traffic (port 8000) from anywhere
  ingress {
    description = "FastAPI app"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Rule: Allow the server to talk to the internet (for updates, etc.)
  # Allow the server to make connections to anywhere on the internet, using any port, using any protocol
  # Download packages, pull docker images, make API calls to external services, update its software
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-sg"
  }

}

# The EC2 server
resource "aws_instance" "app_server" {
  ami           = "ami-0e2c8caa4b6378d8c" # Ubuntu 22.04 in us-east-1
  instance_type = var.instance_type       # Server size (free tier)

  key_name               = aws_key_pair.deployer.key_name
  vpc_security_group_ids = [aws_security_group.app_server.id]

  tags = {
    Name    = "${var.project_name}-server"
    Project = var.project_name
  }

}
