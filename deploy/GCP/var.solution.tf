# Declare variables

variable "solution" {
  type = object({
    name = string
    code = string
    slug = string
  })
}
