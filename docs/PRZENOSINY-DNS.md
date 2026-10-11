# Przenosiny kowalewskasoftware.pl: OVH → Route 53

Cel: strona na `https://kowalewskasoftware.pl` (i `www`) z CloudFront, **bez przerwy
w poczcie Google Workspace**. Na tej domenie są skrzynki root kont AWS — utrata poczty
= utrata resetu haseł do AWS. Dlatego każdy krok da się sprawdzić, zanim pójdzie dalej,
a jedyny nieodwracalny w praktyce krok (zmiana NS) jest na samym końcu.

Stan strefy OVH odczytany 2026-10-11 z `dns111.ovh.net`:

| Nazwa | Typ | Wartość | W Route 53 |
|---|---|---|---|
| apex | MX | `1 smtp.google.com` | ✅ 1:1 |
| apex | TXT | `v=spf1 include:_spf.google.com ~all` | ✅ 1:1 |
| apex | TXT | `google-site-verification=Zqzcx…QFM` | ✅ 1:1 |
| `google._domainkey` | TXT | DKIM Google (2048 bit) | ✅ 1:1 (dzielony na ciągi ≤255) |
| `_dmarc` | TXT | `v=DMARC1; p=none; rua=mailto:dmarc@…` | ✅ 1:1 |
| apex, www | A | `213.186.33.5` (przekierowania OVH) | ❌ → alias CloudFront |
| apex | TXT | `1\|www.kowalewskasoftware.pl` (znacznik OVH) | ❌ |
| www | TXT | `3\|welcome` (znacznik OVH) | ❌ |
| `ftp` | CNAME | apex | ❌ (FTP nigdy nie działał) |

⚠️ Odczyt robiony po znanych nazwach — strefy OVH nie da się pobrać transferem.
**Krok 0 to porównanie z eksportem z panelu.**

## Krok 0 — eksport strefy z OVH (Jolanta)

OVH → Domeny → kowalewskasoftware.pl → **Strefa DNS** → „Zmień w trybie tekstowym”.
Skopiuj całość (nic nie zmieniaj, Anuluj). Każdy rekord, którego nie ma w tabeli wyżej,
musi trafić do `infra/dns.tf` przed krokiem 5.

## Krok 1 — bootstrap konta (raz)

```bash
aws sso login --profile ks-www
aws cloudformation deploy --profile ks-www --region eu-central-1 \
  --stack-name kowalewskasoftware-www-bootstrap \
  --template-file infra/bootstrap/bootstrap.yaml \
  --capabilities CAPABILITY_NAMED_IAM
aws cloudformation describe-stacks --profile ks-www --region eu-central-1 \
  --stack-name kowalewskasoftware-www-bootstrap --query "Stacks[0].Outputs" --output table
```

GitHub → repo → Settings → Environments → **`prod`** → zmienna `AWS_DEPLOY_ROLE_ARN`
= `DeployRoleArn` z wyniku powyżej. Potem merge gałęzi do `main`.

## Krok 2 — etap 1 Terraform (`certyfikat_gotowy = false`)

Actions → „Infra (plan / apply)” → `apply` + `deploy`. Powstaje: strefa z pocztą,
certyfikat (czeka), CloudFront na `*.cloudfront.net`, bucket, budżet.
Potem Actions → „Publikacja strony” — strona działa pod adresem z outputu `cloudfront_adres`.

**Nic w OVH jeszcze się nie zmieniło.** Poczta i obecna domena działają jak dotąd.

## Krok 3 — walidacja certyfikatu przez OVH

Output `walidacja_certyfikatu` → dwa rekordy CNAME (`_xxx.kowalewskasoftware.pl` i
`_yyy.www.kowalewskasoftware.pl`). Dopisz je w strefie OVH (tylko dopisanie, nic nie
usuwasz). Po kilku–kilkunastu minutach certyfikat w ACM (us-east-1) ma status **Issued**.

## Krok 4 — etap 2 Terraform (`certyfikat_gotowy = true`)

Zmiana domyślnej wartości w `infra/variables.tf` → PR → apply. CloudFront dostaje domenę
i certyfikat, strefa Route 53 rekordy A/AAAA. Wciąż nic nie zmienia się dla świata —
publicznie odpowiada OVH.

## Krok 5 — weryfikacja Route 53 PRZED zmianą NS

Pytamy bezpośrednio serwery Route 53 (nazwy z outputu `serwery_nazw`):

```powershell
$ns = "ns-XXX.awsdns-XX.org"
foreach ($t in "MX","TXT","A","AAAA","CAA") { Resolve-DnsName kowalewskasoftware.pl -Type $t -Server $ns -DnsOnly }
Resolve-DnsName google._domainkey.kowalewskasoftware.pl -Type TXT -Server $ns -DnsOnly
Resolve-DnsName _dmarc.kowalewskasoftware.pl -Type TXT -Server $ns -DnsOnly
curl.exe -sI https://kowalewskasoftware.pl --resolve "kowalewskasoftware.pl:443:<IP z A>"
```

MX/SPF/DKIM/DMARC muszą być **identyczne** z OVH (DKIM: po sklejeniu ciągów).

## Krok 5b — wyłączenie DNSSEC w OVH (PRZED zmianą NS!)

OVH domyślnie podpisuje strefę (DNSSEC) i trzyma rekord **DS w rejestrze `.pl`**.
Zmiana NS przy żywym DS = resolvery walidujące (Google, Cloudflare, większość ISP)
odrzucają niepodpisane odpowiedzi Route 53 → **domena i poczta znikają** (SERVFAIL).

1. OVH → Domeny → kowalewskasoftware.pl → Informacje ogólne → Bezpieczeństwo →
   „Zabezpieczenie DNS (DNSSEC)” → wyłącz.
2. Czekaj, aż DS zniknie z serwerów rejestru (źródło prawdy, nie cache):
   `Resolve-DnsName kowalewskasoftware.pl -Type DS -Server a-dns.pl -DnsOnly`
3. Potem odczekaj **TTL starego DS (21600 s = 6 h)** — tyle resolwery mogą go jeszcze pamiętać.
4. Dopiero wtedy krok 6.

Stan z 2026-10-11: DS keytag 12232, algorytm 8, TTL 21600.

## Krok 6 — zmiana NS w OVH

OVH → Domeny → kowalewskasoftware.pl → **Serwery DNS** → „Zmień serwery DNS” →
4 serwery z `serwery_nazw`. Propagacja: do 48 h (TTL NS w `.pl` to zwykle 1 dzień);
w tym czasie część świata pyta OVH, część Route 53 — obie strefy dają tę samą pocztę.

**Wycofanie:** przywrócenie `dns111.ovh.net` / `ns111.ovh.net` w tym samym miejscu.
Strefa OVH zostaje nietknięta do końca propagacji — dlatego wycofanie działa.

## Krok 7 — po propagacji

- Mail testowy na `kontakt@kowalewskasoftware.pl` z **innej** skrzynki niż Gmail Jolanty;
  w nagłówkach odebranego: `dkim=pass`, `spf=pass`, `dmarc=pass`.
- Google Workspace Admin → Aplikacje → Gmail → Uwierzytelnianie: DKIM „Uwierzytelnianie e-maili”.
- `https://kowalewskasoftware.pl`, `https://www…` (→ 301 na apex), `/en/`, `/nie-ma` (404).
- ✅ 2026-10-11: stara strona usunięta z konta dev 708037416948 (3 dystrybucje CloudFront: E1NUSLAP5UY0NP, E37JEBWVTYRWJM, ECYUSRA7S9OEM; buckety phoenixcloud-portfolio-dev i phoenixcloud-portfolio; stan portfolio/terraform.tfstate), sekret AWS_ROLE_ARN skasowany, repo wykreślone z zaufania terraform_role, katalog legacy-dev/ usunięty.
- Później, osobno: DNSSEC w Route 53 (klucz KMS w us-east-1, KSK, potem nowy DS w OVH).
  Kolejność odwrotna niż przy wyłączaniu: najpierw podpisywanie w Route 53, DS na końcu.
