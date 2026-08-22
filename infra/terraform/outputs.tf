output "api_url" {
  description = "Temporary HTTP URL for the API before custom HTTPS domain configuration."
  value       = "http://${aws_lb.api.dns_name}"
}

output "ecr_repository_url" {
  value = aws_ecr_repository.api.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  value = aws_ecs_service.api.name
}

output "rds_endpoint" {
  value     = aws_db_instance.main.address
  sensitive = true
}

output "api_secret_arn" {
  value = aws_secretsmanager_secret.api.arn
}
