# create scheduler for triggering workflows
resource "google_cloud_scheduler_job" "workflow_triggers" {

  name             = jsondecode(templatefile(
    "../../config/naming.patterns.json",
    {
      solution = var.solution,
      services = var.services,
      GCP  = var.GCP
    }
  ))["scheduler"]["etl"]
  description      = var.services.scheduler.etl.desc
  schedule         = var.services.scheduler.etl.schedule
  region           = var.GCP.region
  attempt_deadline = "320s"

  http_target {

    http_method = "POST"
    uri         = "https://workflowexecutions.googleapis.com/v1/${google_workflows_workflow.workflows["etl"].id}/executions"

    oauth_token {
      service_account_email = google_service_account.accounts[var.services.scheduler.etl.serviceAccount].email
      scope = "https://www.googleapis.com/auth/cloud-platform"
    }
  }

}