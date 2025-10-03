output "server_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.app_server.public_ip
}

output "ssh_connection_string" {
  description = "Command to SSH into the server"
  value       = "ssh -i ~/.ssh/ed_gbabeleda ubuntu@${aws_instance.app_server.public_ip}"
}

output "fastapi_url" {
  description = "URL to access FastAPI application"
  value       = "http://${aws_instance.app_server.public_ip}:${var.app_port}"
}

output "server_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.app_server.id
}
