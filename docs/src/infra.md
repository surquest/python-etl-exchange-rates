# Infrastructure

This section describes in details all used Google Cloud Platform services used for running the {{ config.site_name }}.

Following diagram shows the infrastructure used for running the ETL pipeline.

![Infra](./static/drawings/infra.drawio)

The ETL pipeline is orchestrated with the help of Cloud Workflow: **{{ pattern("workflows.etl") }}** triggered by the Cloud Scheduler: **{{ pattern("scheduler.etl") }}**. The Cloud Workflow invokes the Cloud Run service: **{{ pattern("run.services.runner")}}**. 

The data sourced from {{conf.solution.name}} API are in its raw format stored in the Cloud Storage: **{{ pattern("storage.buckets.ingress") }}**. The Cloud Run service is also responsible for transforming and import of the data from Cloud Storage bucket into BigQuery dataset: **{{ pattern("bigquery.datasets.raw") }}**.

# Installation

The installation of the {{ config.site_name }} is fully automated with the help of [Terraform](https://www.terraform.io/). You can use following commands to spin up all the above-mentioned Google Cloud Platform services.

## Prerequisites

If you are going to install this project from your local machine, you need to Docker installed on your machine. Also, you need to have privileged service account with the following roles:

* BigQuery Admin (roles/bigquery.admin)
* Cloud Run Admin (roles/run.admin)
* Cloud Scheduler Admin (roles/cloudscheduler.admin)
* Cloud Storage Admin (roles/storage.admin)
* Service Account Admin (roles/iam.serviceAccountAdmin)
* Service Account Key Admin (roles/iam.serviceAccountKeyAdmin)
* Artifact Registry Admin (roles/artifactregistry.admin)
* Workflow Admin (roles/workflows.admin)
* Secret Manager Admin (roles/secretmanager.admin)

and the keyfile of the service account in the directory `credentials/{ENV}/deployer.keyfile.json` where `{ENV}` is your environment acronym (DEV, TEST, PRE, PROD).

## Before you start

Before you start, you need to adjust also the configuration files for:

* Google Cloud project: `config/config.cloud.google.env.{ENV}.json`,
* Terraform backend: `deploy/terraform/backend.{ENV}.conf`,

where `{ENV}` is your environment acronym (DEV, TEST, PRE, PROD).

---
**NOTE**

If you don't want to use CI/CD pipeline of your VCS, you can use the ready to use PowerShell script `action.run.ps1` to deploy the solution.

---

## Deployment script

The ready to use PowerShell script `action.run.ps1` is located in the root directory of the project. You can use it to deploy the solution. The script is using Docker to run Terraform as well as the Google Cloud SDK to build and push the Docker image to the Google Cloud Artifact Registry and to deploy the Cloud Run service.

It is important to run the actions in this order:

1. **APPLY TERRAFORM** - to create all the required Google Cloud Platform services,
2. **DEPLOY CLOUD RUN** - to build and push the Docker image to the Google Cloud Artifact Registry and to deploy the Cloud Run service.

## CI/CD pipeline

The CI/CD pipeline is fully automated with the help of templated GitLab jobs. If you want to trigger the Google Cloud Platform services deployment, you need to trigger the pipeline with variable `INFRA` set to `DEPLOY`.

Please note, merge into the `master` branch will trigger the pipeline automatically but the publishing of the Docker image to the Google Cloud Artifact Registry and Cloud Run service deployment needs to be triggered manually. Also, creation of the **tag** will trigger the pipeline automatically. The tags need to be in format *0.0.1* where *0.0.1* is the version of the solution. The images as well as the Cloud Run service revisons will be tagged with the version of the solution.
