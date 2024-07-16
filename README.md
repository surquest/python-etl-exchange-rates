# Introduction

This project establishes data pipeline which sources data from ExchangeRatesAPI API documented on (https://exchangeratesapi.io/documentation/) into Analytics Data Mart. At this moment we are sourcing data on daily basis for base currency:

* EUR
* USD

## Features

The current implementation of the data pipeline has the following features:

* Sourcing data from Binance API into BigQuery
* Steering the data pipeline via Google Cloud Workflows
* Tracing the data pipeline via Google Cloud Trace
* Logging the data pipeline via Google Cloud Logging
* Failure alerting for the data pipeline via Google Cloud Monitoring > Alerting
* Deployment of multiple environments (DEV/PROD/...)
* Fully automated via Cloud Scheduler

# Project structure

This project follows structure as outlined below:

```bash
├── config                                    # configuration files for the project
│   ├── subject                               # specification of ETL subjects (including table schema)
│   ├── workflows                             # specification of ETL subjects (including table schema)
│   ├── config.cloud.google.env.{ENV}.json    # Google Cloud Project specification
│   ├── config.cloud.google.servivces.json    # Google Cloud services specification
│   ├── config.solution.json                  # solution/application details (as name, slug, ...)
│   └── naming.patterns.json                  # naming patterns for the GCP resources
├── credentials                               # ATTENTION: not part of git repository but needs to be created locally
├── data                                      # all sample data for the project
├── deploy                                    
│   └── GCP                                   # Terraform scripts for deployment of GCP resources          
├── docs                                      # project documentation for MKDocs published in GitLab Pages          
├── src                                       # source code of the solution/application         
├── test                                      # tests for the solution/application
├── .gitignore                                # files and folders to be ignored by git
├── .gitlab-ci.yml                            # GitLab CI/CD pipeline
├── action.run.ps1                            # hook for running the pipeline jobs locally (apply terraform or deploy cloud run service)
├── apps.base.dockerfile                      # base docker image for the application
├── docs.base.dockerfile                      # base docker image for the documentation
├── docs.requirements.txt                     # requirements specification for the MkDocs documentation 
└── README.md                                 # this file ;o)
```

# Documentation

Complete documentation can be found on [GitLab Pages](http://analytics.docs.wearerealitygames.com/analytical-data-mart/etl/exchange-rates/). The documentation can be also created locally with help of MkDocs in docker.

```powershell
    # NOTE: These commands are in powershell syntax
    
    # creation of the docker image from the Dockerfile
    docker build -t docs/mkdocs-material -f docs.base.dockerfile .
    
    # Serve the documentation locally
    docker run --rm -it `
     --name mkdocs `
     -v ${PWD}:/opt/project `
     -p 8000:8000 `
     docs/mkdocs-material mkdocs serve --dev-addr 0.0.0.0:8000
    
    # Build the documentation as static pages
    docker run --rm -it `
     --name mkdocs-build `
     -v ${PWD}:/opt/project `
     docs/mkdocs-material mkdocs build --strict --verbose --site-dir dist
```

# Local development

The local development environment can be easily create with the help of the docker containers

```powershell
    # NOTE: These commands are in powershell syntax
    
    # creation of the docker image from the Dockerfile
    docker build `
     --tag surquest/etl/bq/exchange-rates:dev `
     --file app.base.dockerfile `
     --target base .
    
    # to be able to run the docker container you need to have the credentials
    # in the file: `credentials/PROD/runner.keyfile.json`
    # you can get the credentials from the Google Cloud Platform
    # https://console.cloud.google.com/security/secret-manager/secret/ETL_CG_RUNNER_PROD_KEYFILE/versions?project=analytics-data-mart
    # or you can get them via the command:
    
    gcloud secrets versions access latest --secret="ETL_CG_RUNNER_PROD_KEYFILE" --out-file="${pwd}/credentials/PROD/runner.keyfile.json"

    # run the docker container locally
    docker run --rm -it `
    --name exchange-rates-dev `
    -v "$(pwd):/opt/project" `
    -e "ENV=LOCAL" `
    -e "ENVIRONMENT=PROD" `
    -e "GOOGLE_APPLICATION_CREDENTIALS=/opt/project/credentials/PROD/runner.keyfile.json" `
    -p 1010:8080 surquest/etl/bq/exchange-rates:dev
```

# Testing

The testing of the application is automated via the GitLab CI/CD as separate stage and job. The CI/CD pipeline is defined in the `.gitlab-ci.yml` file.

If you need to run tests locally, you can use following commands:

```powershell
docker build `
 --tag surquest/etl/bq/exchange-rates:test `
 --file app.base.dockerfile `
 --target test .

docker run --rm -it `
 -v "${pwd}:/opt/project" `
 -e "GOOGLE_APPLICATION_CREDENTIALS=/opt/project/credentials/PROD/runner.keyfile.json" `
 -w "/opt/project/test" `
 surquest/etl/bq/exchange-rates:test pytest
```

## Publish docker image in Docker Hub
docker build `
 --tag surquest/etl/bq/exchange-rates:test `
 --file app.base.dockerfile `
 --target test .

docker push surquest/etl-bq-exchange-rates:latest

# Licence check

This section outlines how to run licence check locally:

```
docker pull pilosus/pip-license-checker
docker run `
 -v "$(pwd):/opt/project" `
 -it --rm pilosus/pip-license-checker `
 java -jar app.jar --exclude 'pylint.*' `
 --requirements '/opt/project/src/app.requirements.txt'
```

# Code quality
docker pull jetbrains/qodana-python

docker run --rm -it -p 8080:8080 `
-v "$(pwd)/src:/data/project/" `
-v "$(pwd)/quality:/data/results/" `
jetbrains/qodana-python --show-report

# Support

In case you have any questions or suggestions please contact us:

* Michal Švarc (michal.svarc@surquest.com)

# To do

* enhance documentation
