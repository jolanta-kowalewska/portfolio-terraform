terraform {
    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "~> 6.0"
        }
    }
    backend "s3" {}
}


provider "aws" {
  region = var.region
}

locals {
    bucket_name_full = "${var.bucket_name}-${var.environment}"
    common_tags = {
        Environment = var.environment
        ManagedBy   = "terraform"
        Project     = "portfolio"    
        Owner       = "Jola"  
    }
    mime_types = {
    "html" = "text/html"
    "css"  = "text/css"
    "js"   = "application/javascript"
    "jpg"  = "image/jpeg"
    "jpeg" = "image/jpeg"
    "png"  = "image/png"
    "ico"  = "image/x-icon"
    "svg"  = "image/svg+xml"

    }
} 

resource "aws_s3_bucket" "portfolio_bucket" {
    bucket = local.bucket_name_full
    tags = local.common_tags
}

resource "aws_s3_bucket_public_access_block" "portfolio_access" {
    bucket = aws_s3_bucket.portfolio_bucket.id

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true

}

resource "aws_cloudfront_origin_access_control" "portfolio_oac" {
  name                              = "default-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "portfolio_distribution" {
  origin {
    domain_name              = aws_s3_bucket.portfolio_bucket.bucket_regional_domain_name
    origin_access_control_id = aws_cloudfront_origin_access_control.portfolio_oac.id
    origin_id                = local.bucket_name_full
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Portfolio CloudFront distribution"
  default_root_object = "index.html"

 

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.bucket_name_full

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  price_class = "PriceClass_100"

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  tags = local.common_tags

  viewer_certificate {
   cloudfront_default_certificate = true
}
}


resource "aws_s3_bucket_policy" "portfolio_bucket_policy" {
  bucket = aws_s3_bucket.portfolio_bucket.bucket
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudFrontServicePrincipal"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.portfolio_bucket.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.portfolio_distribution.arn
          }
        }
      }
    ]
  })
}


resource "aws_s3_object" "portfolio_bucket_object" {
  
  for_each = fileset("website/", "**")

  bucket = aws_s3_bucket.portfolio_bucket.id
  key    = each.value
  source = "website/${each.value}"
  # "Weź nazwę pliku, 
  # wyciągnij rozszerzenie, znajdź odpowiedni MIME type w mapie, 
  # a jeśli nie znajdziesz — użyj domyślnego"
  content_type = lookup(local.mime_types, split(".", each.value)[length(split(".", each.value)) - 1], "application/octet-stream")
  etag         = filemd5("website/${each.value}")
}

resource "terraform_data" "post_object_update" {
  input = sha1(join(",", [
    for f in fileset("website/", "**") : filemd5("website/${f}")
  ]))

  lifecycle {
    action_trigger {

      events = [before_create, before_update]
      actions = [action.aws_cloudfront_create_invalidation.post_object_update]
      
    }
  }

  depends_on = [aws_s3_object.portfolio_bucket_object]
}


action "aws_cloudfront_create_invalidation" "post_object_update" {
  config {
    distribution_id = aws_cloudfront_distribution.portfolio_distribution.id
    paths           = ["/*"]
}
}

