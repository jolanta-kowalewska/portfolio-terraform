# Strefa kowalewskasoftware.pl — przeniesiona z OVH.
#
# ⚠️ Na tej domenie żyje poczta Google Workspace, w tym skrzynki root kont AWS.
# Rekordy pocztowe poniżej to kopia 1:1 strefy OVH z 2026-10-11 (odczyt z dns111.ovh.net).
# Zmiana któregokolwiek z nich = ryzyko utraty poczty, a z nią resetu haseł do AWS.
#
# Świadomie NIE przeniesione z OVH:
#   - A 213.186.33.5 (apex i www) — serwer przekierowań OVH; zastępuje go CloudFront
#   - TXT "1|www.kowalewskasoftware.pl", www TXT "3|welcome" — znaczniki przekierowań OVH
#   - ftp CNAME → apex — wskazywał na serwer przekierowań, FTP nigdy tu nie działał

resource "aws_route53_zone" "glowna" {
  name    = var.domena
  comment = "Strona Kowalewska Software + poczta Google Workspace"
}

locals {
  # Klucz DKIM Google (2048 bit) — dłuższy niż 255 znaków, a tyle mieści jeden ciąg TXT.
  # Route 53 przyjmuje wiele ciągów w jednym rekordzie zapisanych jako "a""b";
  # serwery pocztowe sklejają je z powrotem w jeden klucz.
  dkim_google = "v=DKIM1;k=rsa;p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3d98uHVLorpL0xBXAATVNMmIn7niS1bWRjF5zSRTCGgXEOnbrO07wOG0y4+hPMfh3cPgL5aOKm1pXdqbfGlUM5FTIgBn+Tr0yeveWbk032dZ5onwrw9Oxp1rIEAuOitsav6N9f3xgCyuy6971a5jSPB519AK2ooP7PuZEGiIFiH2LTD1ZPojgE0MWMobKTVdhfyjXkKGIIsmKJn0p85mI4KeDNy3OYab+1fuPynKd+CKyIpHB8tuuUbEM00vvWhxYLRNR+Yqi5Lb3gJk/RQv+009gpWdu8XuGv3wtbUUoNzBuSOL8eMUXRSgatJPmzQFpENiYK/xs+s9JtiaeO0kJQIDAQAB"
}

# --- Poczta (Google Workspace) ---------------------------------------------------

resource "aws_route53_record" "mx" {
  zone_id = aws_route53_zone.glowna.zone_id
  name    = var.domena
  type    = "MX"
  ttl     = 3600
  records = ["1 smtp.google.com"]
}

resource "aws_route53_record" "txt_apex" {
  zone_id = aws_route53_zone.glowna.zone_id
  name    = var.domena
  type    = "TXT"
  ttl     = 3600
  records = [
    "v=spf1 include:_spf.google.com ~all",
    "google-site-verification=Zqzcx_IGVXBIDeOO0w6Gq6Qt5BtH66NUHXiGmAwfQFM",
  ]
}

resource "aws_route53_record" "dkim_google" {
  zone_id = aws_route53_zone.glowna.zone_id
  name    = "google._domainkey.${var.domena}"
  type    = "TXT"
  ttl     = 3600
  records = [join("\"\"", regexall(".{1,255}", local.dkim_google))]
}

resource "aws_route53_record" "dmarc" {
  zone_id = aws_route53_zone.glowna.zone_id
  name    = "_dmarc.${var.domena}"
  type    = "TXT"
  ttl     = 3600
  records = ["v=DMARC1; p=none; rua=mailto:dmarc@${var.domena}"]
}

# --- Kto może wystawiać certyfikaty --------------------------------------------
# Tylko Amazon (ACM). Każdy inny urząd odmówi wystawienia certyfikatu dla tej domeny,
# nawet gdyby ktoś na chwilę przejął jakiś rekord. Google Workspace (poczta) nie
# potrzebuje certyfikatu w tej domenie.

resource "aws_route53_record" "caa" {
  zone_id = aws_route53_zone.glowna.zone_id
  name    = var.domena
  type    = "CAA"
  ttl     = 3600
  records = [
    "0 issue \"amazon.com\"",
    "0 issuewild \";\"",
  ]
}

# --- Strona (etap 2: dopiero gdy CloudFront ma domenę i certyfikat) ---------------

locals {
  rekordy_strony = var.certyfikat_gotowy ? {
    for para in setproduct([var.domena, "www.${var.domena}"], ["A", "AAAA"]) :
    "${para[0]}-${para[1]}" => { nazwa = para[0], typ = para[1] }
  } : {}
}

resource "aws_route53_record" "strona" {
  for_each = local.rekordy_strony

  zone_id = aws_route53_zone.glowna.zone_id
  name    = each.value.nazwa
  type    = each.value.typ

  alias {
    name                   = aws_cloudfront_distribution.strona.domain_name
    zone_id                = aws_cloudfront_distribution.strona.hosted_zone_id
    evaluate_target_health = false
  }
}
