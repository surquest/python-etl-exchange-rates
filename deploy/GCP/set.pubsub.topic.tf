# Create PubSub topic to get Monitoring alerts notifications
resource "google_pubsub_topic" "notifications" {

  for_each = var.services.pubsub.topics

  name = jsondecode(templatefile(
    "../../config/naming.patterns.json",
    {
      solution = var.solution,
      services = var.services,
      GCP  = var.GCP
    }
  ))["pubsub"]["topics"][each.key]

  labels = {
    solution = var.solution.code
  }

  message_retention_duration = each.value.messageRetention

}

resource "google_pubsub_topic_iam_member" "member" {

  for_each = var.services.pubsub.topics
  project = var.GCP.id
  topic = google_pubsub_topic.notifications[each.key].name
  role = "roles/pubsub.publisher"
  member = "serviceAccount:service-${var.GCP.number}@gcp-sa-monitoring-notification.iam.gserviceaccount.com"
}