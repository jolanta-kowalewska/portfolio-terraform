# Strona: prywatny bucket S3 → CloudFront (OAC). Pliki wgrywa workflow strona.yml
# (aws s3 sync), nie Terraform — Terraform odpowiada tylko za infrastrukturę.

resource "aws_s3_bucket" "strona" {
  bucket = "kowalewskasoftware-www-${var.konto_aws}"
}

resource "aws_s3_bucket_public_access_block" "strona" {
  bucket                  = aws_s3_bucket.strona.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "strona" {
  bucket = aws_s3_bucket.strona.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "strona" {
  bucket = aws_s3_bucket.strona.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Wersjonowanie = cofnięcie złej publikacji bez gita. Stare wersje znikają po 30 dniach.
resource "aws_s3_bucket_versioning" "strona" {
  bucket = aws_s3_bucket.strona.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "strona" {
  bucket = aws_s3_bucket.strona.id
  rule {
    id     = "stare-wersje"
    status = "Enabled"
    filter {}
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

resource "aws_s3_bucket_policy" "strona" {
  bucket = aws_s3_bucket.strona.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "TylkoCloudFront"
        Effect    = "Allow"
        Principal = { Service = "cloudfront.amazonaws.com" }
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.strona.arn}/*"
        Condition = {
          StringEquals = { "AWS:SourceArn" = aws_cloudfront_distribution.strona.arn }
        }
      },
      {
        Sid       = "TylkoTLS"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource  = [aws_s3_bucket.strona.arn, "${aws_s3_bucket.strona.arn}/*"]
        Condition = { Bool = { "aws:SecureTransport" = "false" } }
      },
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.strona]
}

resource "aws_cloudfront_origin_access_control" "strona" {
  name                              = "kowalewskasoftware-www"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# www → apex (301) oraz katalogi → index.html. S3 przez OAC nie zna „indeksu katalogu",
# więc bez tego /en/ zwraca 403 (= nasza strona 404).
resource "aws_cloudfront_function" "adresy" {
  name    = "kowalewskasoftware-www-adresy"
  runtime = "cloudfront-js-2.0"
  publish = true
  code = <<-JS
    function handler(event) {
      var req = event.request;
      var host = req.headers.host ? req.headers.host.value : "";
      if (host.indexOf("www.") === 0) {
        return {
          statusCode: 301,
          statusDescription: "Moved Permanently",
          headers: { location: { value: "https://" + host.substring(4) + req.uri } }
        };
      }
      if (req.uri.endsWith("/")) {
        req.uri += "index.html";
      } else if (req.uri.split("/").pop().indexOf(".") === -1) {
        return {
          statusCode: 301,
          statusDescription: "Moved Permanently",
          headers: { location: { value: req.uri + "/" } }
        };
      }
      return req;
    }
  JS
}

# Nagłówki bezpieczeństwa. CSP jest ścisłe: strona nie ma inline skryptów ani stylów,
# a fonty są hostowane lokalnie — nic nie ładuje się z zewnątrz.
resource "aws_cloudfront_response_headers_policy" "bezpieczenstwo" {
  name = "kowalewskasoftware-www-naglowki"

  security_headers_config {
    content_security_policy {
      content_security_policy = join("; ", [
        "default-src 'none'",
        "script-src 'self'",
        "style-src 'self'",
        "img-src 'self' data:", # ikona karty to SVG w data: URL
        "font-src 'self'",
        "base-uri 'none'",
        "form-action 'none'",
        "frame-ancestors 'none'",
        "upgrade-insecure-requests",
      ])
      override = true
    }
    strict_transport_security {
      access_control_max_age_sec = 63072000
      include_subdomains         = true
      override                   = true
    }
    content_type_options {
      override = true
    }
    frame_options {
      frame_option = "DENY"
      override     = true
    }
    referrer_policy {
      referrer_policy = "strict-origin-when-cross-origin"
      override        = true
    }
  }

  custom_headers_config {
    items {
      header   = "Permissions-Policy"
      value    = "camera=(), microphone=(), geolocation=(), interest-cohort=()"
      override = true
    }
  }
}

data "aws_cloudfront_cache_policy" "optymalna" {
  name = "Managed-CachingOptimized"
}

resource "aws_cloudfront_distribution" "strona" {
  enabled             = true
  is_ipv6_enabled     = true
  http_version        = "http2and3"
  comment             = "kowalewskasoftware.pl"
  default_root_object = "index.html"
  price_class         = "PriceClass_100"
  aliases             = var.certyfikat_gotowy ? [var.domena, "www.${var.domena}"] : []

  origin {
    domain_name              = aws_s3_bucket.strona.bucket_regional_domain_name
    origin_id                = "s3-strona"
    origin_access_control_id = aws_cloudfront_origin_access_control.strona.id
  }

  default_cache_behavior {
    target_origin_id           = "s3-strona"
    viewer_protocol_policy     = "redirect-to-https"
    allowed_methods            = ["GET", "HEAD"]
    cached_methods             = ["GET", "HEAD"]
    compress                   = true
    cache_policy_id            = data.aws_cloudfront_cache_policy.optymalna.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.bezpieczenstwo.id

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.adresy.arn
    }
  }

  # Brakujący plik: S3 przez OAC zwraca 403 (nie 404 — nie dajemy ListBucket).
  # Oba kody → nasza strona 404 z prawdziwym kodem 404.
  dynamic "custom_error_response" {
    for_each = [403, 404]
    content {
      error_code            = custom_error_response.value
      response_code         = 404
      response_page_path    = "/404.html"
      error_caching_min_ttl = 60
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  dynamic "viewer_certificate" {
    for_each = var.certyfikat_gotowy ? [1] : []
    content {
      acm_certificate_arn      = aws_acm_certificate_validation.strona[0].certificate_arn
      ssl_support_method       = "sni-only"
      minimum_protocol_version = "TLSv1.2_2021"
    }
  }

  dynamic "viewer_certificate" {
    for_each = var.certyfikat_gotowy ? [] : [1]
    content {
      cloudfront_default_certificate = true
    }
  }
}
