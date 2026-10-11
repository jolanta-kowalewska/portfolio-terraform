terraform {
  # Zakres zamknięty — ta sama wersja co w .github/workflows/infra.yml. Stan zapisany
  # nowszym Terraformem nie da się odczytać starszym, więc rozjazd ma padać od razu.
  required_version = "~> 1.14.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.54"
    }
  }

  # Konfiguracja częściowa: bucket podaje się przy init (prod.s3.tfbackend).
  # Blokada stanu natywnie w S3 (use_lockfile) — bez tabeli DynamoDB.
  backend "s3" {}
}

provider "aws" {
  region = "eu-central-1"

  # Bezpiecznik: apply na jakimkolwiek innym koncie (np. Integry) pada przed zmianą.
  allowed_account_ids = [var.konto_aws]

  default_tags {
    tags = local.tagi
  }
}

# Certyfikat dla CloudFront musi być w us-east-1 — to wymóg CloudFront, nie wybór.
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  allowed_account_ids = [var.konto_aws]

  default_tags {
    tags = local.tagi
  }
}

locals {
  tagi = {
    Project   = "kowalewskasoftware-www"
    ManagedBy = "terraform"
    Repo      = "jolanta-kowalewska/portfolio-terraform"
  }
}
