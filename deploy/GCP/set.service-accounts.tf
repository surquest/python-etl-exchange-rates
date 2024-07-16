# -> create service accounts
resource "google_service_account" "accounts" {

  for_each      = var.services.IAM.serviceAccounts

  account_id = jsondecode(templatefile(
    "../../config/naming.patterns.json",
    {
      solution = var.solution,
      services = var.services,
      GCP  = var.GCP
    }
  ))["IAM"]["serviceAccounts"][each.key]

  display_name  = "${each.value.name} (${upper(var.GCP.env)})"
  description   = "${each.value.desc} for ${upper(var.GCP.env)}"

}

locals {
  service_account_roles = flatten([
    for key, value in var.services.IAM.serviceAccounts: [
      for item in value.roles: {
        idx             = key
        role            = item
      }
  ]
  ])
}

# -> grant IAM roles for service accounts
resource "google_project_iam_member" "sa_iam_binding" {

  count = length(local.service_account_roles)

  project = var.GCP.id
  role    = local.service_account_roles[count.index].role
  member  = "serviceAccount:${google_service_account.accounts[local.service_account_roles[count.index].idx].email}"
}

# -> create the account keys
resource "google_service_account_key" "keys" {

  for_each      = var.services.IAM.serviceAccounts

  service_account_id = google_service_account.accounts[each.key].name

}

# -> export the keys data
data "google_service_account_key" "keys_data" {

  for_each      = var.services.IAM.serviceAccounts

  name            = google_service_account_key.keys[each.key].name
  public_key_type = "TYPE_X509_PEM_FILE"

}

# -> save the service account key locally
resource "local_file" "key_files" {

  for_each      = var.services.IAM.serviceAccounts

  content  = base64decode(google_service_account_key.keys[each.key].private_key)
  filename = "../../credentials/${upper(var.GCP.env)}/${var.services.IAM.serviceAccounts[each.key].code}.keyfile.json"

}

# -> create secrets with stores credentials
resource "google_secret_manager_secret" "secret_key_files" {

  for_each      = var.services.IAM.serviceAccounts

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
      )["secrets"]["keyfiles"][each.key]
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
resource "google_secret_manager_secret_version" "secret_key_files_versions" {

  depends_on = [local_file.key_files]

  for_each      = var.services.IAM.serviceAccounts

  secret = google_secret_manager_secret.secret_key_files[each.key].id
  secret_data = google_service_account_key.keys[each.key].private_key

}

# -> grant access to the secrets for the Runner Service Account
resource "google_secret_manager_secret_iam_binding" "store_secrets_iam" {

  for_each      = var.services.IAM.serviceAccounts

  secret_id = google_secret_manager_secret.secret_key_files[each.key].id
  role = "roles/secretmanager.secretAccessor"
  members = [
    "serviceAccount:${google_service_account.accounts["runner"].email}"
  ]

}
