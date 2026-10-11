variable "konto_aws" {
  description = "Konto Kowalewska Software WWW. Provider odmówi pracy na każdym innym."
  type        = string
  default     = "298712672271"
}

variable "domena" {
  type    = string
  default = "kowalewskasoftware.pl"
}

variable "certyfikat_gotowy" {
  description = <<-EOT
    Etap 2 przenosin. false (etap 1): powstaje strefa z pocztą, certyfikat (czeka na
    walidację) i CloudFront na adresie *.cloudfront.net. true (etap 2): po wystawieniu
    certyfikatu — domena podpięta pod CloudFront i rekordy A/AAAA w strefie.
    NS w OVH przełączamy dopiero po etapie 2, więc strona działa od pierwszej sekundy.
  EOT
  type    = bool
  default = false
}

variable "email_alertow" {
  description = "Adres alertów budżetu."
  type        = string
  default     = "aws-www-prod@kowalewskasoftware.pl"
}

variable "budzet_usd" {
  description = "Miesięczny budżet konta. Realny koszt strony + DNS to ~1-2 USD."
  type        = number
  default     = 10
}
