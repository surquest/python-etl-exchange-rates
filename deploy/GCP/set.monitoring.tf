resource "google_monitoring_notification_channel" "pubsub_channel" {
  display_name = var.services.monitoring.notificationChannels.pubsub.name
  type         = "pubsub"
  labels = {
    topic = google_pubsub_topic.notifications["alerting"].id
  }
  force_delete = false
}

resource "google_monitoring_alert_policy" "alert_policy_workflow" {
  display_name = var.services.monitoring.alertPolicies.etl.name
  combiner     = "OR"
  conditions {
    display_name = var.services.monitoring.alertPolicies.etl.condition.name
    condition_threshold {
      filter     = join(" AND ", [
        "resource.type = \"workflows.googleapis.com/Workflow\"",
        "resource.labels.workflow_id = \"${google_workflows_workflow.workflows["etl"].name}\"",
        "metric.type = \"workflows.googleapis.com/finished_execution_count\"",
        "metric.labels.status = \"FAILED\""
      ])
      duration   = var.services.monitoring.alertPolicies.etl.condition.duration
      comparison = var.services.monitoring.alertPolicies.etl.condition.comparison
      aggregations {
        alignment_period   = var.services.monitoring.alertPolicies.etl.condition.aggregations.alignmentPeriod
        per_series_aligner = var.services.monitoring.alertPolicies.etl.condition.aggregations.perSeriesAligner
      }
      trigger {
        count = var.services.monitoring.alertPolicies.etl.condition.trigger.count
      }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.pubsub_channel.name
  ]

  enabled = true
}

