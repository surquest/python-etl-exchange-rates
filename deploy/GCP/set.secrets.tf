# Create secrets within the GCP Secret Manager

resource "google_secret_manager_secret" "apikey_secret" {

    secret_id   = upper(
        jsondecode(
            templatefile(
            "../../config/naming.patterns.json",
            {
                solution = var.solution,
                services = var.services,
                GCP  = var.GCP
            }
            )
        )["secrets"]["misc"]["apiKey"]
    )

    labels = {
        project = var.solution.code
        environment = var.GCP.env
    }

    replication {
        auto {}
    }

}

# -> add versions to secrets for stores credentials
resource "google_secret_manager_secret_version" "apikey_secret_versions" {

  secret = google_secret_manager_secret.apikey_secret.id
  secret_data = "Uoz7Su97WPzkxKd9epx3ebd3a7Fx20is" # the secret version needs to be manually updated in the GCP console for security reasons 

}

# -> grant access to the secrets for the Runner Service Account
resource "google_secret_manager_secret_iam_binding" "apikey_secret_iam" {

  secret_id = google_secret_manager_secret.apikey_secret.id
  role = "roles/secretmanager.secretAccessor"
  members = [
    "serviceAccount:${google_service_account.accounts["runner"].email}"
  ]

}
