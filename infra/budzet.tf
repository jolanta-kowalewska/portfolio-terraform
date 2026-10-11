# Alarm kosztów. Strona + DNS to ~1-2 USD/mies., więc przekroczenie budżetu oznacza
# coś nienormalnego (np. sztuczny ruch na CloudFront) — mail, nie wyłączenie strony.
resource "aws_budgets_budget" "konto" {
  name         = "kowalewskasoftware-www-miesiecznie"
  budget_type  = "COST"
  limit_amount = tostring(var.budzet_usd)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 50
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.email_alertow]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.email_alertow]
  }
}
