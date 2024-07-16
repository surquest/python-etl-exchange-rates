# Build docker image

#terraform {
#  required_providers {
#    docker = {
#      source  = "kreuzwerker/docker"
#      version = "3.0.2"
#    }
#  }
#}
#
## Configure the docker provider
#provider "docker" {
#  host = "unix:///var/run/docker.sock"
#}
#
#
#resource "docker_image" "runner" {
#  name = var.services.run.services.runner.image
#  build {
#    context   = "../../"
#    dockerfile = "../../app.base.dockerfile"
#    target = "app"
#    tag       = [var.services.run.services.runner.image]
#  }
#}
#
#resource "docker_registry_image" "runner" {
#  name          = docker_image.runner.name
#  keep_remotely = true
#}

# Push docker image to GCR

## Cloud Run deployment
#resource "google_cloud_run_service" "runner" {
#
#  name = jsondecode(templatefile(
#    "../../config/naming.patterns.json",
#    {
#      solution = var.solution,
#      services = var.services,
#      GCP      = var.GCP
#    }
#  )).run.services.runner
#  location = var.GCP.region
#
#  metadata {
#    annotations = {
#      "run.googleapis.com/ingress" = "internal-and-cloud-load-balancing"
#    }
#  }
#
#  template {
#
#    spec {
#      containers {
#        image = var.services.run.services.runner.image
#        env {
#          name  = "PATH_PREFIX"
#          value = join("/", [
#            "/api",
#            jsondecode(templatefile(
#              "../../config/naming.patterns.json",
#              {
#                solution = var.solution,
#                services = var.services,
#                GCP      = var.GCP
#              }
#            )).run.services.runner,
#            var.services.run.services.runner.version
#          ]
#          )
#        }
#        env {
#          name  = "ENVIRONMENT"
#          value = upper(var.GCP.env)
#        }
#      }
#      service_account_name = google_service_account.accounts["runner"].email
#    }
#
#  }
#
#  traffic {
#    percent         = 100
#    latest_revision = true
#    tag             = var.services.run.services.runner.version
#  }
#
#}
#
#data "google_iam_policy" "no_auth" {
#  binding {
#    role    = "roles/run.invoker"
#    members = [
#      "allUsers",
#    ]
#  }
#}
#
#resource "google_cloud_run_service_iam_policy" "no_auth" {
#  location = google_cloud_run_service.runner.location
#  project  = google_cloud_run_service.runner.project
#  service  = google_cloud_run_service.runner.name
#
#  policy_data = data.google_iam_policy.no_auth.policy_data
#}