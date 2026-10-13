"""Buduje portfolio PL (/) i EN (/en/) z wersji produkcyjnej strony.
Wygląd bez zmian; treść: założycielka Kowalewska Software, IntegraHolistic, MindData.
Style/skrypt w osobnych plikach (ścisłe CSP), kroje pisma lokalnie (bez Google Fonts)."""
import re
from pathlib import Path

W = Path(__file__).resolve().parents[1] / "website"
# Bazą jest ZAWSZE wersja pobrana z produkcji, nie website/index.html — ten plik
# skrypt sam nadpisuje (PL), więc drugie uruchomienie tłumaczyłoby tłumaczenie.
src = (Path(__file__).resolve().parent / "zrodlo-produkcja-2026-05.html").read_text(encoding="utf-8")


def rx(fragment: str) -> str:
    """Wzorzec odporny na różnice w białych znakach (wcięcia, łamanie wierszy)."""
    return r"\s+".join(re.escape(t) for t in fragment.split())


def rep(s: str, a: str, b: str, ile: int = 1) -> str:
    n = len(re.findall(rx(a), s))
    assert n == ile, f"{n}× zamiast {ile}×: {a[:70]!r}"
    return re.sub(rx(a), lambda _: b, s)


# ---------- style i skrypt do plików ----------
css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
js = re.search(r"<script>(.*?)</script>", src, re.S).group(1)
fonty = []
for rodzina, plik, waga, styl in [
    ("Space Mono", "space-mono", 400, "normal"), ("Space Mono", "space-mono", 700, "normal"),
    ("DM Sans", "dm-sans", 300, "normal"), ("DM Sans", "dm-sans", 400, "normal"),
    ("DM Sans", "dm-sans", 500, "normal"), ("DM Sans", "dm-sans", 700, "normal"),
    ("DM Sans", "dm-sans", 300, "italic"),
]:
    for sub, zakres in (("latin-ext", "U+0100-024F, U+1E00-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF"),
                        ("latin", "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD")):
        fonty.append(f"@font-face{{font-family:'{rodzina}';font-style:{styl};font-weight:{waga};font-display:swap;"
                     f"src:url(/assets/fonts/{plik}-{sub}-{waga}-{styl}.woff2) format('woff2');unicode-range:{zakres}}}")
dodatki = """
/* Przełącznik języka i drobne dodatki (wydzielone z atrybutów style=). */
.lang-switch { font-family: 'Space Mono', monospace; font-size: .75rem; letter-spacing: .1em; margin-left: 1.5rem;
  padding: .25rem .6rem; border: 1px solid currentColor; border-radius: 4px; text-decoration: none; color: inherit; opacity: .8; }
.lang-switch:hover { opacity: 1; }
.section-divider.center { margin: 1rem auto 0; }
.company-id { display: block; margin-top: .4rem; font-family: 'Space Mono', monospace; font-size: .75rem; opacity: .7; }
"""
(W / "assets" / "styles.css").write_text("\n".join(fonty) + "\n" + css.strip() + "\n" + dodatki, encoding="utf-8", newline="\n")
(W / "assets" / "site.js").write_text(js.strip() + "\n", encoding="utf-8", newline="\n")

body = src[src.index("<body>"):]
body = re.sub(r"\s*<script>.*?</script>\s*", "\n", body, flags=re.S)
body = body.replace('<div class="section-divider" style="margin: 1rem auto 0;"></div>', '<div class="section-divider center"></div>')
body = body.replace('src="photo.jpg"', 'src="/photo.jpg" width="200" height="200"')
body = body.replace('target="_blank"', 'target="_blank" rel="noopener"')

# ---------- EN: nowa treść ----------
en = body
en = rep(en, '<li><a href="#contact">Contact</a></li>\n        </ul>',
         '<li><a href="#contact">Contact</a></li>\n        </ul>\n        <a href="/" class="lang-switch" hreflang="pl" lang="pl">PL</a>')
en = rep(en, '<p class="hero-label">☁ Above the Clouds</p>', '<p class="hero-label">☁ Kowalewska Software</p>')
en = rep(en, '<p class="hero-title">Cloud Engineer · AWS Certified · Python Developer · VMware Veteran</p>',
         '<p class="hero-title">Founder · AWS Cloud Engineer · Solutions Architect Associate · VMware Veteran</p>')
en = rep(en, '<p class="hero-tagline">From VMware to AWS Serverless ☁️</p>',
         '<p class="hero-tagline">Building software for holistic beauty and trichology clinics — on AWS ☁️</p>')
en = rep(en, '<a href="#projects" class="btn btn-primary">View Projects</a>', '<a href="#projects" class="btn btn-primary">See Projects</a>')
en = rep(en, '<a href="#contact" class="btn btn-outline">Let\'s Connect</a>', '<a href="#contact" class="btn btn-outline">Get in Touch</a>')
en = rep(en, """<p class="timeline-role">🚀 AWS Cloud Engineer · Serverless · IaC</p>
                    <p class="timeline-company">Self-directed learning · Open to new role</p>
                    <p class="timeline-desc">
                        Started Python on January 26, 2026. Passed AWS Solutions Architect Associate (SAA-C03)
                        in April with 809/1000. Building production-grade serverless apps with Lambda, DynamoDB,
                        Step Functions, Terraform Workspaces and GitHub Actions CI/CD.
                        The destination: Cloud / DevOps Engineer in public cloud.
                    </p>""", """<p class="timeline-role">🚀 Founder · Kowalewska Software</p>
                    <p class="timeline-company">IntegraHolistic · MindData · AWS Serverless</p>
                    <p class="timeline-desc">
                        Started Python on January 26, 2026 and passed AWS Solutions Architect Associate (SAA-C03)
                        in April with 809/1000. Since summer I have been building IntegraHolistic — a production SaaS
                        for holistic cosmetology and trichology clinics, created together with a practicing
                        cosmetologist. Health data, done properly: a dedicated AWS account in an Organization,
                        SCPs, Identity Center with MFA, KMS encryption and a daily security watchdog.
                    </p>""")
en = rep(en, """<div class="project-card featured fade-in">
                    <span class="project-status featured">★ FEATURED · LIVE</span>""", """<div class="project-card featured fade-in">
                    <span class="project-status featured">★ MY COMPANY · LIVE</span>
                    <h3 class="project-title">🌿 IntegraHolistic — Software for Holistic Clinics</h3>
                    <p class="project-desc">
                        Production SaaS for holistic cosmetology and trichology clinics, co-created with a practicing
                        cosmetologist. Client records and interviews, the Holistic Action Plan generator, consents signed
                        on a tablet, treatment packages, team schedule, revenue and commissions, voice notes.
                        Health data under GDPR art. 9: dedicated production account in an AWS Organization with SCPs,
                        Identity Center with MFA, KMS encryption, WAF, EU-only data residency and a daily security report.
                    </p>
                    <div class="project-tech">
                        <span>Lambda</span>
                        <span>API Gateway</span>
                        <span>DynamoDB</span>
                        <span>Cognito MFA</span>
                        <span>KMS</span>
                        <span>CloudFront</span>
                        <span>WAF</span>
                        <span>Route 53</span>
                        <span>SES</span>
                        <span>Bedrock</span>
                        <span>Transcribe</span>
                        <span>Organizations · SCP</span>
                        <span>Terraform</span>
                        <span>GitHub Actions</span>
                        <span>React</span>
                        <span>Python</span>
                    </div>
                    <div class="project-links">
                        <a href="https://www.integraholistic.pl" target="_blank" rel="noopener" class="project-link primary">→ integraholistic.pl</a>
                        <a href="https://www.integraholistic.pl/#film" target="_blank" rel="noopener" class="project-link">→ 80-second film</a>
                    </div>
                </div>

                <div class="project-card fade-in">
                    <span class="project-status live">✓ MY COMPANY · LIVE</span>
                    <h3 class="project-title">🧠 MindData — for Psychology Practices</h3>
                    <p class="project-desc">
                        Secure web app for psychologists and psychotherapists: session notes that become immutable
                        once signed, digital GDPR consents with full history, appointment calendar (in person and online)
                        and an AI assistant that turns rough notes into a structured summary. AES-256 encryption, MFA,
                        audit log, data stored in the EU (Frankfurt).
                    </p>
                    <div class="project-tech">
                        <span>AWS Serverless</span>
                        <span>Cognito MFA</span>
                        <span>KMS</span>
                        <span>Bedrock</span>
                        <span>React</span>
                        <span>Terraform</span>
                    </div>
                    <div class="project-links">
                        <a href="https://www.minddata.pl" target="_blank" rel="noopener" class="project-link primary">→ minddata.pl</a>
                    </div>
                </div>

                <div class="project-card fade-in">
                    <span class="project-status live">✓ LIVE</span>""")
en = rep(en, """<p class="contact-intro fade-in">
                I'm actively looking for a Cloud Engineer or DevOps Engineer role.
                If you're building cloud infrastructure and need someone who understands
                both the theory and the operational reality — let's talk.
            </p>""", """<p class="contact-intro fade-in">
                Running a clinic and want to see IntegraHolistic with your own products and treatments?
                Or building something on AWS and need someone who knows both the theory and the
                operational reality? Let's talk.
            </p>""")
en = rep(en, 'href="mailto:brzojr@gmail.com"', 'href="mailto:kontakt@kowalewskasoftware.pl"')
en = rep(en, '<span class="open-to-work">Open to new opportunities</span>',
         '<span class="open-to-work">Kowalewska Software</span>\n                <span class="company-id">NIP PL6652851454</span>')
en = rep(en, '<p>Built by <span>Jola Kowalewska</span> · Hosted on <span>AWS S3</span> · 2026</p>',
         '<p>Built by <span>Jola Kowalewska</span> · Hosted on <span>AWS S3 + CloudFront</span> · 2026</p>')


def head(lang, tytul, opis, sciezka, inny):
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tytul}</title>
    <meta name="description" content="{opis}">
    <link rel="canonical" href="https://kowalewskasoftware.pl{sciezka}">
    <link rel="alternate" hreflang="pl" href="https://kowalewskasoftware.pl/">
    <link rel="alternate" hreflang="en" href="https://kowalewskasoftware.pl/en/">
    <link rel="alternate" hreflang="x-default" href="https://kowalewskasoftware.pl/">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://kowalewskasoftware.pl{sciezka}">
    <meta property="og:title" content="{tytul}">
    <meta property="og:description" content="{opis}">
    <meta property="og:image" content="https://kowalewskasoftware.pl/photo.jpg">
    <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E☁%3C/text%3E%3C/svg%3E">
    <link rel="preload" href="/assets/fonts/space-mono-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="stylesheet" href="/assets/styles.css">
    <script src="/assets/site.js" defer></script>
</head>
"""


(W / "en").mkdir(exist_ok=True)
(W / "en" / "index.html").write_text(
    head("en", "Jola Kowalewska — Founder of Kowalewska Software · AWS Cloud Engineer",
         "I build IntegraHolistic (holistic cosmetology and trichology clinics) and MindData (psychology practices) on AWS. 14 years in private cloud, AWS Solutions Architect Associate.",
         "/en/", "pl") + en, encoding="utf-8", newline="\n")

# ---------- PL: tłumaczenie wersji EN ----------
pl = en
PARY = [
    ('<a href="/" class="lang-switch" hreflang="pl" lang="pl">PL</a>', '<a href="/en/" class="lang-switch" hreflang="en" lang="en">EN</a>'),
    ('<li><a href="#journey">Journey</a></li>', '<li><a href="#journey">Droga</a></li>'),
    ('<li><a href="#skills">Skills</a></li>', '<li><a href="#skills">Umiejętności</a></li>'),
    ('<li><a href="#certs">Certs</a></li>', '<li><a href="#certs">Certyfikaty</a></li>'),
    ('<li><a href="#projects">Projects</a></li>', '<li><a href="#projects">Projekty</a></li>'),
    ('<li><a href="#contact">Contact</a></li>', '<li><a href="#contact">Kontakt</a></li>'),
    ('<p class="hero-title">Founder · AWS Cloud Engineer · Solutions Architect Associate · VMware Veteran</p>',
     '<p class="hero-title">Założycielka · AWS Cloud Engineer · Solutions Architect Associate · VMware Veteran</p>'),
    ('<p class="hero-tagline">Building software for holistic beauty and trichology clinics — on AWS ☁️</p>',
     '<p class="hero-tagline">Tworzę oprogramowanie dla gabinetów kosmetologii i trychologii holistycznej — na AWS ☁️</p>'),
    ('class="btn btn-primary">See Projects</a>', 'class="btn btn-primary">Zobacz projekty</a>'),
    ('class="btn btn-outline">Get in Touch</a>', 'class="btn btn-outline">Napisz do mnie</a>'),
    ('<span>scroll</span>', '<span>przewiń</span>'),
    ('<span class="section-label">🛫 Flight Path</span>', '<span class="section-label">🛫 Trasa lotu</span>'),
    ('<h2 class="section-title">My Journey</h2>', '<h2 class="section-title">Moja droga</h2>'),
    ('<p class="timeline-role">🎓 Student → First Steps in IT</p>', '<p class="timeline-role">🎓 Studia → pierwsze kroki w IT</p>'),
    ('<p class="timeline-company">University of Technology and Life Sciences, Bydgoszcz</p>',
     '<p class="timeline-company">Uniwersytet Technologiczno-Przyrodniczy w Bydgoszczy</p>'),
    ("""BSc in Data Communications. First IT experience during Polish EU Presidency — first-line support.
                        Troubleshooting became my natural path from day one.""",
     """Inżynier teleinformatyki. Pierwsze doświadczenie w IT przy polskiej prezydencji w UE — wsparcie pierwszej linii.
                        Rozwiązywanie problemów od pierwszego dnia stało się moją naturalną drogą."""),
    ("""Nearly 5 years supporting Polish VMware clients. Deep expertise in vSphere troubleshooting,
                        incident resolution, and enterprise infrastructure. Learned that understanding the problem
                        is half the solution.""",
     """Prawie 5 lat wsparcia polskich klientów VMware. Głęboka znajomość diagnozowania vSphere,
                        rozwiązywania incydentów i infrastruktury korporacyjnej. Nauczyłam się, że zrozumienie
                        problemu to połowa rozwiązania."""),
    ("""7 years designing and executing private cloud deployments — vSphere, vRO, vRA, Dell VBlock, RCM upgrades.
                        Planning full-scale upgrade cycles for enterprise clients across Europe.
                        From engineer to architect.""",
     """7 lat projektowania i wdrażania chmur prywatnych — vSphere, vRO, vRA, Dell VBlock, aktualizacje RCM.
                        Planowanie pełnych cykli aktualizacji dla klientów korporacyjnych w całej Europie.
                        Od inżynierki do architektki."""),
    ('<p class="timeline-year">2026 — Now</p>', '<p class="timeline-year">2026 — teraz</p>'),
    ('<p class="timeline-role">🚀 Founder · Kowalewska Software</p>', '<p class="timeline-role">🚀 Założycielka · Kowalewska Software</p>'),
    ("""Started Python on January 26, 2026 and passed AWS Solutions Architect Associate (SAA-C03)
                        in April with 809/1000. Since summer I have been building IntegraHolistic — a production SaaS
                        for holistic cosmetology and trichology clinics, created together with a practicing
                        cosmetologist. Health data, done properly: a dedicated AWS account in an Organization,
                        SCPs, Identity Center with MFA, KMS encryption and a daily security watchdog.""",
     """Pythona zaczęłam 26 stycznia 2026, a w kwietniu zdałam AWS Solutions Architect Associate (SAA-C03)
                        z wynikiem 809/1000. Od lata tworzę IntegraHolistic — produkcyjną aplikację SaaS
                        dla gabinetów kosmetologii i trychologii holistycznej, razem z praktykującą kosmetolożką.
                        Dane o zdrowiu zrobione porządnie: osobne konto AWS w organizacji, polityki SCP,
                        Identity Center z MFA, szyfrowanie KMS i codzienny raport bezpieczeństwa."""),
    ("""\"I like to crack problems and put together puzzles.
                    Troubleshooting is my natural path — step by step to the solution.
                    That satisfaction of <em>'It works!'</em> drives me every day.
                    After 14 years in private cloud — it's time to rise higher.\"""",
     """„Lubię rozgryzać problemy i układać puzzle.
                    Rozwiązywanie problemów to moja naturalna droga — krok po kroku do celu.
                    Ta satysfakcja z <em>„Działa!”</em> napędza mnie każdego dnia.
                    Po 14 latach w chmurze prywatnej — czas wznieść się wyżej.”"""),
    ('<cite>— Why IT? Why AWS?</cite>', '<cite>— Dlaczego IT? Dlaczego AWS?</cite>'),
    ('<h2 class="section-title">Skills & Technologies</h2>', '<h2 class="section-title">Umiejętności i technologie</h2>'),
    ('<p class="skill-card-title">AWS — Hands-on</p>', '<p class="skill-card-title">AWS — w praktyce</p>'),
    ('<p class="skill-card-title">Python — Building</p>', '<p class="skill-card-title">Python — buduję</p>'),
    ('<p class="skill-card-title">VMware — Expert</p>', '<p class="skill-card-title">VMware — ekspertka</p>'),
    ('<span class="section-label">📜 Leveling Up</span>', '<span class="section-label">📜 Kolejne poziomy</span>'),
    ('<h2 class="section-title">Certifications</h2>', '<h2 class="section-title">Certyfikaty</h2>'),
    ('Amazon Web Services · SAA-C03 · April 2026 · Score 809/1000', 'Amazon Web Services · SAA-C03 · kwiecień 2026 · wynik 809/1000'),
    ('<span class="cert-badge">PASSED</span>', '<span class="cert-badge">ZDANY</span>'),
    ('<span class="section-label">🚀 Deployed in the Cloud</span>', '<span class="section-label">🚀 Wdrożone w chmurze</span>'),
    ('<h2 class="section-title">Projects</h2>', '<h2 class="section-title">Projekty</h2>'),
    ('<span class="project-status featured">★ MY COMPANY · LIVE</span>', '<span class="project-status featured">★ MOJA FIRMA · DZIAŁA</span>'),
    ('<h3 class="project-title">🌿 IntegraHolistic — Software for Holistic Clinics</h3>',
     '<h3 class="project-title">🌿 IntegraHolistic — aplikacja dla gabinetów holistycznych</h3>'),
    ("""Production SaaS for holistic cosmetology and trichology clinics, co-created with a practicing
                        cosmetologist. Client records and interviews, the Holistic Action Plan generator, consents signed
                        on a tablet, treatment packages, team schedule, revenue and commissions, voice notes.
                        Health data under GDPR art. 9: dedicated production account in an AWS Organization with SCPs,
                        Identity Center with MFA, KMS encryption, WAF, EU-only data residency and a daily security report.""",
     """Produkcyjna aplikacja SaaS dla gabinetów kosmetologii i trychologii holistycznej, współtworzona
                        z praktykującą kosmetolożką. Kartoteka i wywiad, generator Planu Holistycznego Działania, zgody
                        podpisywane na tablecie, pakiety zabiegów, grafik zespołu, utarg i prowizje, dyktowanie notatek.
                        Dane o zdrowiu (RODO art. 9): osobne konto produkcyjne w organizacji AWS z politykami SCP,
                        Identity Center z MFA, szyfrowanie KMS, WAF, dane wyłącznie w UE i codzienny raport bezpieczeństwa."""),
    ('class="project-link">→ 80-second film</a>', 'class="project-link">→ film (80 s)</a>'),
    ('<span class="project-status live">✓ MY COMPANY · LIVE</span>', '<span class="project-status live">✓ MOJA FIRMA · DZIAŁA</span>'),
    ('<h3 class="project-title">🧠 MindData — for Psychology Practices</h3>', '<h3 class="project-title">🧠 MindData — aplikacja dla gabinetów psychologicznych</h3>'),
    ("""Secure web app for psychologists and psychotherapists: session notes that become immutable
                        once signed, digital GDPR consents with full history, appointment calendar (in person and online)
                        and an AI assistant that turns rough notes into a structured summary. AES-256 encryption, MFA,
                        audit log, data stored in the EU (Frankfurt).""",
     """Bezpieczna aplikacja dla psychologów i psychoterapeutów: notatki z sesji, które po podpisaniu stają się
                        niezmienne, cyfrowe zgody RODO z pełną historią, kalendarz wizyt (stacjonarnych i online)
                        oraz asystent AI, który porządkuje notatki z brudnopisu. Szyfrowanie AES-256, MFA, dziennik
                        audytowy, dane w UE (Frankfurt)."""),
    ('<span class="project-status live">✓ LIVE</span>', '<span class="project-status live">✓ DZIAŁA</span>'),
    ('<h3 class="project-title">🌱 Plant Inventory App — Serverless on AWS</h3>', '<h3 class="project-title">🌱 Plant Inventory App — serverless na AWS</h3>'),
    ("""Production-grade serverless application for managing garden care plans.
                        Step Functions orchestrates 11 Lambdas to generate yearly care schedules using
                        Anthropic Claude AI, then verifies them monthly against weather forecasts via
                        OpenWeatherMap and sends HTML email proposals through SES.
                        Plant database (~1800 species) imported from Wikidata SPARQL.
                        Frontend hosted on S3 + CloudFront with HTTPS. Full IaC with Terraform Workspaces
                        and zero-keys CI/CD via GitHub Actions + OIDC.""",
     """Produkcyjna aplikacja serverless do planów pielęgnacji ogrodu. Step Functions steruje
                        11 funkcjami Lambda, które z pomocą Anthropic Claude AI układają roczny kalendarz pielęgnacji,
                        co miesiąc weryfikują go z prognozą pogody (OpenWeatherMap) i wysyłają propozycje mailem przez SES.
                        Baza ~1800 gatunków roślin zaimportowana z Wikidata (SPARQL). Front na S3 + CloudFront z HTTPS,
                        całość w Terraform Workspaces, CI/CD bez kluczy przez GitHub Actions + OIDC."""),
    ('class="project-link primary">→ Live Demo</a>', 'class="project-link primary">→ Wersja demo</a>'),
    ("""Python CLI tool for managing EC2 instances — list, start, stop, reboot and terminate
                        with selective instance targeting. Includes audit logging to S3 with caller identity
                        tracking via AWS STS. Built with OOP, error handling and daily log rotation.""",
     """Narzędzie CLI w Pythonie do zarządzania instancjami EC2 — wyświetlanie, start, stop, restart i usuwanie
                        wybranych instancji. Dziennik audytowy w S3 z tożsamością wywołującego (AWS STS).
                        Programowanie obiektowe, obsługa błędów i codzienna rotacja logów."""),
    ("""Full-featured currency converter with live exchange rates via API, conversion history
                        stored in S3, and advanced Pandas analytics reports. Menu-driven CLI with duplicate
                        detection and S3 file management.""",
     """Przelicznik walut z bieżącymi kursami z API, historią przeliczeń w S3 i raportami
                        analitycznymi w Pandas. Interfejs z menu, wykrywanie duplikatów i zarządzanie plikami w S3."""),
    ("""Python CLI tool that queries AWS infrastructure and saves a JSON health report to S3.
                        Checks: EC2 instance IDs and states, S3 bucket sizes via CloudWatch, IAM user count
                        with last login, and ELB load balancer types and states.""",
     """Narzędzie CLI w Pythonie, które odpytuje infrastrukturę AWS i zapisuje raport stanu (JSON) w S3:
                        instancje EC2 i ich stany, rozmiary bucketów S3 z CloudWatch, użytkownicy IAM z ostatnim
                        logowaniem oraz typy i stany load balancerów ELB."""),
    ("""Python CLI tool that compares EC2 On-Demand prices across AWS regions using the
                        AWS Pricing API. Highlights the cheapest region for any instance type and OS.
                        Live prices reflect current On-Demand rates with OS license costs included.""",
     """Narzędzie CLI w Pythonie porównujące ceny EC2 On-Demand między regionami AWS (AWS Pricing API).
                        Wskazuje najtańszy region dla danego typu instancji i systemu, z kosztem licencji systemu."""),
    ('<span class="project-status wip">⚡ COMING NEXT</span>', '<span class="project-status wip">⚡ NASTĘPNY KROK</span>'),
    ("""Next learning project — containerized application on Amazon EKS,
                        deeper Terraform with modules, and CKA preparation.
                        Building hands-on Kubernetes experience to complement serverless skills.""",
     """Następny projekt do nauki — aplikacja w kontenerach na Amazon EKS, Terraform z modułami
                        i przygotowanie do CKA. Praktyka z Kubernetesem jako uzupełnienie serverless."""),
    ('<span class="section-label">📡 Let\'s Connect</span>', '<span class="section-label">📡 Bądźmy w kontakcie</span>'),
    ('<h2 class="section-title">Get In Touch</h2>', '<h2 class="section-title">Kontakt</h2>'),
    ("""Running a clinic and want to see IntegraHolistic with your own products and treatments?
                Or building something on AWS and need someone who knows both the theory and the
                operational reality? Let's talk.""",
     """Prowadzisz gabinet i chcesz zobaczyć IntegraHolistic na swoich produktach i zabiegach?
                Albo budujesz coś na AWS i potrzebujesz kogoś, kto zna i teorię, i codzienną praktykę
                utrzymania? Porozmawiajmy."""),
    ('<p>Built by <span>Jola Kowalewska</span> · Hosted on <span>AWS S3 + CloudFront</span> · 2026</p>',
     '<p>Zbudowała <span>Jola Kowalewska</span> · Hosting: <span>AWS S3 + CloudFront</span> · 2026</p>'),
]
for a, b in PARY:
    pl = rep(pl, a, b, ile=len(re.findall(rx(a), pl)) or 1)
(W / "index.html").write_text(
    head("pl", "Jola Kowalewska — założycielka Kowalewska Software · AWS Cloud Engineer",
         "Tworzę na AWS IntegraHolistic (gabinety kosmetologii i trychologii holistycznej) i MindData (gabinety psychologiczne). 14 lat w chmurze prywatnej, AWS Solutions Architect Associate.",
         "/", "en") + pl, encoding="utf-8", newline="\n")

zostalo = [x for x in ("Journey", "Skills", "Projects", "Get In Touch", "Open to", "LIVE", "PASSED", "Hands-on")
           if re.search(rf">\s*[^<]*\b{re.escape(x)}", pl)]
print("PL zbudowane; podejrzane angielskie resztki:", zostalo)
