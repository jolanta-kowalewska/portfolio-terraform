variable "environment" {
    description = "Environment to deploy"
    type = string
    default = "prod"
}

variable "bucket_name" {
    description = "Bucket name"
    type = string
    default = "portfolio"
}

variable "region" {
    description = "AWS region"
    type = string
    default = "eu-central-1"
}

