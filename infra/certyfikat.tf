# Certyfikat dla apex + www (us-east-1, wymóg CloudFront).
#
# Rekordy walidacyjne trafiają do strefy Route 53 od razu — ACM odnawia certyfikat sam,
# ale tylko dopóki te rekordy są widoczne publicznie, więc muszą zostać na zawsze.
# Przed przełączeniem NS publicznie widać jednak OVH, nie Route 53 — dlatego w etapie 1
# ten sam CNAME (output `walidacja_certyfikatu`) dopisuje się też ręcznie w OVH.

resource "aws_acm_certificate" "strona" {
  provider = aws.us_east_1

  domain_name               = var.domena
  subject_alternative_names = ["www.${var.domena}"]
  validation_method         = "DNS"
  key_algorithm             = "EC_prime256v1"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "walidacja" {
  for_each = {
    for o in aws_acm_certificate.strona.domain_validation_options : o.domain_name => o
  }

  zone_id         = aws_route53_zone.glowna.zone_id
  name            = each.value.resource_record_name
  type            = each.value.resource_record_type
  ttl             = 300
  records         = [each.value.resource_record_value]
  allow_overwrite = true
}

# Etap 2: czeka, aż certyfikat ma status ISSUED. W etapie 1 nie istnieje — inaczej
# apply wisiałby do skutku, zanim ktokolwiek dopisze rekord w OVH.
resource "aws_acm_certificate_validation" "strona" {
  count    = var.certyfikat_gotowy ? 1 : 0
  provider = aws.us_east_1

  certificate_arn         = aws_acm_certificate.strona.arn
  validation_record_fqdns = [for r in aws_route53_record.walidacja : r.fqdn]
}
