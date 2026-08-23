output "api_url" {
  description = "Temporary HTTP URL for the API before custom HTTPS domain configuration."
  value       = "http://${aws_lb.api.dns_name}"
}

output "api_https_url" {
  description = "HTTPS URL for the production API through CloudFront."
  value       = "https://${aws_cloudfront_distribution.api.domain_name}"
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

output "github_deploy_role_arn" {
  description = "Set this value as the GitHub Actions production secret AWS_DEPLOY_ROLE_ARN."
  value       = aws_iam_role.github_deploy.arn
}
