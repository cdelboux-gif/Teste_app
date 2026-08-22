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
  type    = number
  default = 1
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
  type    = bool
  default = true
}
