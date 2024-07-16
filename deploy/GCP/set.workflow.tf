# create workflows
resource "google_workflows_workflow" "workflows" {

#  depends_on = [google_cloud_run_service.runner]

  for_each = var.services.workflows

  name = jsondecode(templatefile(
    "../../config/naming.patterns.json",
    {
      solution = var.solution,
      services = var.services,
      GCP  = var.GCP
    }
  ))["workflows"][each.key]

  region          = var.GCP.region
  description     = each.value.desc
    service_account = google_service_account.accounts[each.value.serviceAccount].id

    source_contents = templatefile(
    "../../config/workflows/${each.value.source}",
    {
      solution = var.solution,
      services = var.services,
      GCP      = var.GCP
    }
  )

}