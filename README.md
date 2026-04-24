# AWS S3 + CloudFront Static Site — Terraform

Static portfolio site deployed on AWS using Infrastructure as Code (Terraform).  
Private S3 bucket served through CloudFront CDN with HTTPS and automated cache invalidation.

## Architecture

```
Browser → CloudFront (HTTPS) → OAC → S3 (private bucket)
```

| Component | Details |
|---|---|
| **S3** | Private bucket, block all public access |
| **CloudFront** | CDN, redirect HTTP→HTTPS, PriceClass_100 |
| **OAC** | Origin Access Control, sigv4 signing |
| **Terraform** | IaC, hashicorp/aws ~6.0, for_each, filemd5 tracking |

## Features

- ✅ Private S3 bucket — no direct public access
- ✅ HTTPS enforced via CloudFront
- ✅ Automated cache invalidation on file change
- ✅ All files tracked by `filemd5()` — Terraform detects changes automatically
- ✅ Common tags on all resources

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.14
- [AWS CLI](https://aws.amazon.com/cli/) configured (`aws configure`)
- AWS account with appropriate permissions

## Usage

```bash
# Clone the repo
git clone https://github.com/jolanta-kowalewska/portfolio-terraform.git
cd portfolio-terraform

# Create your tfvars
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Deploy
terraform init
terraform plan
terraform apply
```

## Variables

| Variable | Description | Default |
|---|---|---|
| `bucket_name` | S3 bucket name | `phoenixcloud-portfolio` |
| `environment` | Deployment environment | `dev` |
| `region` | AWS region | `eu-central-1` |

## Outputs

| Output | Description |
|---|---|
| `portfolio_cloudfront_url` | CloudFront distribution URL |
| `portfolio_bucket` | S3 bucket name |

## Project Structure

```
.
├── main.tf                 # S3, CloudFront, OAC, bucket policy, invalidation
├── variables.tf            # Input variables
├── outputs.tf              # Output values
├── terraform.tfvars        # Variable values (not committed)
├── .terraform.lock.hcl     # Provider version lock
├── .gitignore
└── website/                # Static site files
    └── index.html
```

## Author

**Jola Kowalewska** — Cloud Engineer  
AWS Certified Solutions Architect – Associate (SAA-C03)  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jolanta-kowalewska-b1281799/)
