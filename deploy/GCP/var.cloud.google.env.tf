# Declare Google Cloud variables

variable "GCP" {
  type = object({
    id = string
    name = string
    number = number
    location = string
    region = string
    zone = string
    env = string
  })
}
