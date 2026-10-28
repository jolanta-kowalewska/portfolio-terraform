# DNSSEC dla kowalewskasoftware.pl

Podpisywanie strefy w Route 53 + rekord DS w rejestrze .pl (przez OVH, gdzie jest domena).
Szablon: `infra/dnssec/dnssec.yaml` (CloudFormation, us-east-1).

> ⚠️ Na tej domenie żyje poczta Google Workspace ze skrzynkami root kont AWS.
> Błąd w DNSSEC = SERVFAIL całej domeny, czyli także poczty. Dlatego kolejność kroków
> jest sztywna, a DS w OVH dodaje się **najwcześniej 48 h** po włączeniu podpisywania.

## Krok 1. Włączenie podpisywania (Route 53)

```bash
aws sso login --profile ks-www
ZONE=$(aws route53 list-hosted-zones-by-name --profile ks-www \
  --dns-name kowalewskasoftware.pl --query "HostedZones[0].Id" --output text | cut -d/ -f3)

aws cloudformation deploy --profile ks-www --region us-east-1 \
  --stack-name kowalewskasoftware-www-dnssec \
  --template-file infra/dnssec/dnssec.yaml \
  --parameter-overrides HostedZoneId=$ZONE
```

Potwierdź subskrypcję SNS z maila na `aws-www-prod@kowalewskasoftware.pl`.

Sprawdzenie (strefa podpisana, rejestr jeszcze nic o tym nie wie — to normalne):

```bash
dig +dnssec kowalewskasoftware.pl DNSKEY @ns-28.awsdns-03.com   # 2 klucze (KSK 257 + ZSK 256) i RRSIG
dig +dnssec kowalewskasoftware.pl MX @ns-28.awsdns-03.com       # MX + RRSIG
```

Na tym etapie nic się nie może zepsuć: bez DS w rejestrze resolwery traktują strefę
jak niepodpisaną.

## Krok 2. Odczekaj 48 h

Najdłuższy TTL w strefie to NS (172 800 s). Resolwery muszą zdążyć zapomnieć
niepodpisane odpowiedzi, zanim rejestr zacznie wymagać podpisów.

## Krok 3. DS w OVH

```bash
aws route53 get-dnssec --profile ks-www --hosted-zone-id $ZONE \
  --query "KeySigningKeys[0].{KeyTag:KeyTag,Flag:Flag,Algorytm:SigningAlgorithmType,KluczPubliczny:PublicKey,DS:DSRecord}"
```

OVH → Domeny → kowalewskasoftware.pl → **Rekordy DS** → Edytuj → Dodaj:

| Pole w OVH | Wartość |
|---|---|
| Key Tag | `KeyTag` z wyniku |
| Flag | 257 (KSK) |
| Algorytm | 13 (ECDSAP256SHA256) |
| Klucz publiczny | `PublicKey` z wyniku (bez spacji) |

Rejestr .pl publikuje DS zwykle w ciągu kilku godzin.

## Krok 4. Weryfikacja

```bash
dig kowalewskasoftware.pl DS @b-dns.pl          # DS widoczny w rejestrze
dig +dnssec kowalewskasoftware.pl MX @1.1.1.1   # flaga "ad" = odpowiedź zwalidowana
```

Plus https://dnsviz.net/d/kowalewskasoftware.pl/dnssec/ — cały łańcuch na zielono.
Na koniec mail testowy z zewnętrznej skrzynki (nie z Gmaila Jolanty) w obie strony.

## Alarmy

Dwa alarmy CloudWatch (us-east-1) wysyłają mail przez SNS:
`DNSSECInternalFailure` i `DNSSECKeySigningKeysNeedingAction`. Każdy z nich przy
opublikowanym DS oznacza, że domena za chwilę przestanie się rozwiązywać — reagować od razu.

## Wycofanie (tylko w tej kolejności)

1. Usuń DS w OVH.
2. Odczekaj, aż DS zniknie z rejestru, plus TTL DS (w .pl 6 h) z zapasem.
3. Dopiero teraz wyłącz podpisywanie (`aws route53 disable-hosted-zone-dnssec`), potem
   dezaktywuj KSK.
4. Klucz KMS ma w polityce zakaz `DisableKey`/`ScheduleKeyDeletion` — żeby go usunąć,
   najpierw świadomie zmień politykę.

Nigdy odwrotnie: wyłączenie podpisywania albo klucza przy żywym DS = SERVFAIL domeny.
