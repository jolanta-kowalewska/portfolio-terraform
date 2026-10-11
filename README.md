# kowalewskasoftware.pl — static site on AWS, fully in code

Company site of Kowalewska Software (PL + EN), served from a dedicated AWS account
inside an AWS Organization. Everything — DNS zone with Google Workspace mail records,
TLS certificate, CDN, security headers, budget alarm — is Terraform; deployments run
from GitHub Actions via OIDC, with no long-lived AWS keys anywhere.

## Architecture

```
Browser ─▶ Route 53 (apex + www, A/AAAA alias)
        ─▶ CloudFront (HTTP/2+3, TLS 1.2+, ACM cert, CloudFront Function)
        ─▶ OAC (SigV4) ─▶ S3 (private, versioned, TLS-only)
```

| Area | Details |
|---|---|
| **Account isolation** | Dedicated workload account in an AWS Organization; SCP limits regions to eu-central-1 / us-east-1; provider pinned with `allowed_account_ids` |
| **DNS** | Route 53 zone; Google Workspace MX / SPF / DKIM (2048-bit, split TXT) / DMARC; CAA restricted to Amazon |
| **TLS** | ACM (ECDSA P-256) in us-east-1, DNS validation, HSTS 2 years |
| **Edge** | CloudFront Function: `www` → apex 301, directory index rewrite; real 404 page (OAC 403 → 404) |
| **Headers** | Strict CSP (`default-src 'none'`, self-hosted fonts, no inline code), X-Frame-Options DENY, nosniff, Referrer-Policy, Permissions-Policy |
| **Caching** | Fonts immutable (1 year), CSS/JS 1 hour, HTML always revalidated; invalidation on publish |
| **CI/CD** | GitHub OIDC → IAM role trusted only for this repo's `prod` environment; role has no IAM permissions |
| **State** | S3 backend with native lockfile (no DynamoDB), versioned, TLS-only |
| **Cost** | AWS Budgets alert; expected cost ~1–2 USD/month |
| **Privacy** | No analytics, no cookies, no third-party requests |

## Layout

```
infra/bootstrap/bootstrap.yaml   one-off CloudFormation: state bucket + OIDC role
infra/*.tf                       DNS, certificate, CloudFront, S3, budget
website/                         the site (PL at /, EN at /en/)
tools/buduj_strone.py            builds both language versions
.github/workflows/infra.yml      terraform plan on push, apply on manual dispatch
.github/workflows/strona.yml     publishes website/ and invalidates the CDN
legacy-dev/                      previous version (CloudFront default domain), kept until decommissioned
```

## Deploy

1. Bootstrap once: `aws cloudformation deploy --template-file infra/bootstrap/bootstrap.yaml ...`
2. GitHub environment `prod` with variable `AWS_DEPLOY_ROLE_ARN`.
3. `Infra (plan / apply)` → apply; then `Publikacja strony`.

DNS migration runbook (Polish): [docs/PRZENOSINY-DNS.md](docs/PRZENOSINY-DNS.md).

## Author

**Jola Kowalewska** — founder of Kowalewska Software, AWS Cloud Engineer
AWS Certified Solutions Architect – Associate (SAA-C03)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jolanta-kowalewska-b1281799/)
