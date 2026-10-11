output "serwery_nazw" {
  description = "Te 4 serwery wpisuje się w OVH (Domeny → Serwery DNS) — DOPIERO po etapie 2."
  value       = aws_route53_zone.glowna.name_servers
}

output "walidacja_certyfikatu" {
  description = "Etap 1: te CNAME dopisać też w strefie OVH, żeby ACM wystawił certyfikat przed przełączeniem NS."
  value = {
    for o in aws_acm_certificate.strona.domain_validation_options :
    o.domain_name => "${o.resource_record_name} CNAME ${o.resource_record_value}"
  }
}

output "cloudfront_adres" {
  description = "Podgląd strony przed przełączeniem domeny."
  value       = "https://${aws_cloudfront_distribution.strona.domain_name}"
}

output "cloudfront_id" {
  value = aws_cloudfront_distribution.strona.id
}

output "bucket_strony" {
  value = aws_s3_bucket.strona.id
}
