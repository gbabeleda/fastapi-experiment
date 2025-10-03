variable "aws_region" {
  description = "AWS region to create resources in"
  type        = string
  default     = "us-east-1"

}

variable "instance_type" {
  description = "EC2 instance type (size of server)"
  type        = string
  default     = "t2.micro"
}

variable "ssh_key_path" {
  description = "Path to SSH public key"
  type        = string
  default     = "~/.ssh/ed_gbabeleda.pub"
}

variable "app_port" {
  description = "Port that FastAPI will run on"
  type        = number
  default     = 8000
}

variable "project_name" {
  description = "Name of project for tagging"
  type        = string
  default     = "fastapi-dev"
}
