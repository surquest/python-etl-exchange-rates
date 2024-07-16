# Array of environments to deploy to
$ENVIRONMENTS = @("PROD")
$ACTIONS = @("APPLY TERRAFORM", "DEPLOY CLOUD RUN")
$PREFIX = "etl"

# Supporting functions
function Select-Option {
    param (
        [Parameter(Mandatory=$true)]
        [string[]]$Options
    )

    $selectedOption = $null
    while ($selectedOption -eq $null) {
        Write-Host "Please select one of the available options:"
        for ($i = 0; $i -lt $Options.Length; $i++) {
            Write-Host "$($i + 1): $($Options[$i])"
        }
        $input = Read-Host
        if ([int]::TryParse($input, [ref]$null)) {
            $index = [int]$input - 1
            if ($index -ge 0 -and $index -lt $Options.Length) {
                $selectedOption = $Options[$index]
            }
        }
    }

    return $selectedOption
}

$ACTION = Select-Option -Options $ACTIONS
$ENV = Select-Option -Options $ENVIRONMENTS
$ENV_L = $ENV.ToLower()

Write-Output "Action: ${ACTION} to apply on ${ENV} environment"


# Extract variables from config files
$GCP = (Get-Content "./config/config.cloud.google.env.${ENV}.json" | Out-String | ConvertFrom-Json).GCP
$SOL = (Get-Content "./config/config.solution.json" | Out-String | ConvertFrom-Json).solution
$SERVICES = (Get-Content "./config/config.cloud.google.services.json" | Out-String | ConvertFrom-Json).services
$SERVICE = $SOL.code
$VERSION = $SERVICES.run.services.runner.version
$SERVICE_SLUG = $SOL.slug
$PROJECT = $GCP.id
$REGION = $GCP.region


if($ACTION -eq "DEPLOY CLOUD RUN"){
    # configure Google Cloud
    gcloud auth activate-service-account --key-file="./credentials/${ENV}/deployer.keyfile.json"
    gcloud config set project $GCP.id
    gcloud config set compute/zone $GCP.zone

    # build and push docker image
    docker build `
     -t "us-central1-docker.pkg.dev/${PROJECT}/${PREFIX}--${ENV_L}/${SERVICE}/${ENV_L}" `
     -f app.base.dockerfile `
     --target app .

    # login to GCP Container registry
    cat credentials/${ENV}/deployer.keyfile.json | docker login -u _json_key --password-stdin "https://us-central1-docker.pkg.dev"

    # push docker image to GCP Artifact Registry
    docker push "us-central1-docker.pkg.dev/${PROJECT}/${PREFIX}--${ENV_L}/${SERVICE}/${ENV_L}"

    # deploy to Google Cloud Run
    gcloud run deploy "${PREFIX}--${SERVICE}--${ENV_L}" `
     --region $REGION `
     --tag $VERSION `
     --image "us-central1-docker.pkg.dev/${PROJECT}/${PREFIX}--${ENV_L}/${SERVICE}/${ENV_L}:latest" `
     --service-account "${PREFIX}--${SERVICE_SLUG}-runner--${ENV}@${project}.iam.gserviceaccount.com" `
     --set-env-vars="ENVIRONMENT=${ENV}" `
     --set-env-vars="PATH_PREFIX=/api/${PREFIX}--${SERVICE}--${ENV_L}/${VERSION}" `
     --ingress internal-and-cloud-load-balancing `
     --platform managed `
     --allow-unauthenticated
}

if($ACTION -eq "APPLY TERRAFORM"){


   Write-Output "$(Get-Date) Stage: Terraform Init - Started"
   # Initiate Terraform
   docker run --rm -i `
    -v "${pwd}:/tf" `
    -e "GOOGLE_APPLICATION_CREDENTIALS=/tf/credentials/${ENV}/deployer.keyfile.json" `
    hashicorp/terraform:latest `
    "-chdir=/tf/deploy/GCP" init "-backend-config=/tf/deploy/GCP/backend.${ENV}.conf" -reconfigure

   Write-Output "$(Get-Date) Stage: Terraform Init - Finished"


   # Validate Terraform
   docker run --rm -i `
    -v "${pwd}:/tf" `
    -e "GOOGLE_APPLICATION_CREDENTIALS=/tf/credentials/${ENV}/deployer.keyfile.json" `
    hashicorp/terraform:latest `
    "-chdir=/tf/deploy/GCP" validate

    # Import Terraform
#    docker run --rm -i `
#     -v "${pwd}:/tf" `
#     -v "/var/run/docker.sock:/var/run/docker.sock" `
#     -e "GOOGLE_APPLICATION_CREDENTIALS=/tf/credentials/${ENV}/deployer.keyfile.json" `
#     hashicorp/terraform:latest `
#      "-chdir=/tf/deploy/GCP" import   `
#      "-var-file=/tf/config/config.solution.json" `
#      "-var-file=/tf/config/config.cloud.google.env.${ENV}.json" `
#      "-var-file=/tf/config/config.cloud.google.services.json" `
#      google_bigquery_dataset.datasets[0] analytics-data-mart/adm_exchange_rates_raw

    # Apply Terraform
    docker run --rm -i `
     -v "${pwd}:/tf" `
     -v "/var/run/docker.sock:/var/run/docker.sock" `
     -e "GOOGLE_APPLICATION_CREDENTIALS=/tf/credentials/${ENV}/deployer.keyfile.json" `
     hashicorp/terraform:latest `
      "-chdir=/tf/deploy/GCP" apply `
      "-var-file=/tf/config/config.solution.json" `
      "-var-file=/tf/config/config.cloud.google.env.${ENV}.json" `
      "-var-file=/tf/config/config.cloud.google.services.json"
}


