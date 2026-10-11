output "portfolio_cloudfront_url" {
  value = "https://${aws_cloudfront_distribution.portfolio_distribution.domain_name}"
  description = "Cloudfront distribution URL for portfolio website hosted on S3"
}

output "portfolio_bucket" {
  value = aws_s3_bucket.portfolio_bucket.bucket
  description = "Bucket name for portfolio website hosted on S3"
}