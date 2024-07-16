# create big query datasets > google play data
resource "google_bigquery_dataset" "datasets" {

  for_each = var.services.bigquery.datasets

  dataset_id = jsondecode(templatefile(
    "../../config/naming.patterns.json",
    {
      solution = var.solution,
      services = var.services,
      GCP      = var.GCP
    }
  )).bigquery.datasets[each.key]

  friendly_name              = each.value.name
  description                = each.value.desc
  location                   = var.GCP.location
  delete_contents_on_destroy = each.value.deletionProtection

  labels = {
    solution = var.solution.code
  }

  access {
    role          = "OWNER"
    user_by_email = google_service_account.accounts["runner"].email
  }

  access {
    role          = "OWNER"
    user_by_email = "adm--deployer@analytics-data-mart.iam.gserviceaccount.com"
  }

  access {
    role          = "OWNER"
    user_by_email = "michal.svarc@reality.co"
  }

  access {
    role          = "READER"
    group_by_email = "analysts@reality.co"
  }

  dynamic "access" {
    for_each = each.value.access
    content {
        role          = access.value.role
        user_by_email = access.value.email
    }
  }

}

#locals {
#  dataset_permission = flatten([
#    for datasetKey, dataset in var.services.bigquery.datasets : [
#      for accessIdx, access in dataset.access : {
#        "datasetKey" : datasetKey,
#        "role" : access.role,
#        "type" : access.type,
#        "email" : access.email
#      }
#    ]
#  ])
#}
#
#resource "google_bigquery_dataset_iam_member" "permissions" {
#
#  count = length(local.dataset_permission)
#
#  dataset_id = google_bigquery_dataset.datasets[local.dataset_permission[count.index].datasetKey].dataset_id
#  role       = local.dataset_permission[count.index].role
#  member     = join(":", [
#    local.dataset_permission[count.index].type,
#    local.dataset_permission[count.index].email,
#  ])
#}

locals {

  currencies = ["EUR", "USD"]

}

resource "google_bigquery_table" "views" {

  depends_on = [
    google_bigquery_dataset.datasets,
#    google_bigquery_dataset_iam_member.permissions
  ]

  count = length(local.currencies)

  dataset_id     = google_bigquery_dataset.datasets["raw"].dataset_id
  table_id       = upper(local.currencies[count.index])


  view {
    use_legacy_sql = false
    query = templatefile(
      "../../config/templates/current.exchange-rates.sql",
      {
        dataset  = google_bigquery_dataset.datasets["raw"].dataset_id
        currency = local.currencies[count.index]
      }
    )

  }

}

