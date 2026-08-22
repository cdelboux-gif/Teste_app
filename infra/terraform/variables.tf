variable "project_name" {
  type    = string
  default = "vitapoint"
}

variable "environment" {
  type    = string
  default = "production"
}

variable "aws_region" {
  type    = string
  default = "sa-east-1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.40.0.0/16"
}

variable "db_name" {
  type    = string
  default = "vitapoint"
}

variable "db_username" {
  type    = string
  default = "vitapoint"
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "ecs_cpu" {
  type    = number
  default = 256
}

variable "ecs_memory" {
  type    = number
  default = 512
}

variable "desired_count" {
  description = "Bootstrap task count. Keep at zero until a backend image is pushed to ECR."
  type        = number
  default     = 0
}

variable "container_port" {
  type    = number
  default = 8000
}

variable "image_tag" {
  type    = string
  default = "latest"
}

variable "cors_origins" {
  type    = string
  default = "https://example.invalid"
}

variable "github_repository" {
  type    = string
  default = "cdelboux-gif/Teste_app"
}

variable "github_branch" {
  type    = string
  default = "main"
}

variable "create_github_oidc_provider" {
  description = "Create the GitHub OIDC provider only when the AWS account does not already have one."
  type        = bool
  default     = false
}
