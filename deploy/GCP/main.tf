provider "google" {

	project 	= var.GCP.id
	region  	= var.GCP.region
	zone    	= var.GCP.zone

	batching {
		enable_batching = false
	}

}


terraform {

    backend "gcs" {
		prefix = "adm/etl/exchange-rates"
    }

}
