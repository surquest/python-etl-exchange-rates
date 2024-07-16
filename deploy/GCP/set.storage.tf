# -> create storage buckets
resource "google_storage_bucket" "buckets" {

  for_each      = var.services.storage.buckets

  name           = jsondecode(templatefile(
    "../../config/naming.patterns.json",
    {
      solution = var.solution,
      services = var.services,
      GCP  = var.GCP
    }
  ))["storage"]["buckets"][each.key]

  location      = var.GCP.location
  uniform_bucket_level_access = true
  force_destroy = true

  lifecycle_rule {

      condition {
          age = each.value.lifecycle.age
      }
      action {
          type = each.value.lifecycle.actionType
      }
  }

}

# bind permissions to the service account for Cloud CQL database instance
resource "google_storage_bucket_iam_member" "buckets_permissions" {

    for_each      = var.services.storage.buckets

  	bucket 	      = google_storage_bucket.buckets[each.key].name
  	role 		  = "roles/storage.objectAdmin"
  	member        = "serviceAccount:${google_service_account.accounts["runner"].email}"
}
