variable "services" {

  type = object({

    IAM = object({
      serviceAccounts = object({
        runner = object({
          name  = string
          desc  = string
          code  = string
          roles = list(string)
        })
      })
    })

    storage = object({
      buckets = object({
        ingress = object({
          desc      = string
          code      = string
          lifecycle = object({
            age        = number
            actionType = string
          })
        })
      })
    })


    secretManager = object({
      secrets = object({
        FX = object({
          code = string
        })
        APIKEY = object({
          code = string
        })
      })
    })

    bigquery = object({
      datasets = object({
        raw = object({
          name               = string
          desc               = string
          code               = string
          deletionProtection = bool
          access             = list(
            object({
              role  = string
              type  = string
              email = string
            })
          )
        })
      })
    })

    workflows = map(
      object({
        desc           = string
        serviceAccount = string
        source         = string
        subWorkflow    = optional(string)

        trigger = optional(
          object({
            schedule = string
            timeZone = string
          })
        )
      })
    )

    scheduler = map(
      object({
        desc           = string
        serviceAccount = string
        schedule       = string
        timeZone       = string
      })
    )

    run = object({
      services = map(
        object({
          image   = string
          version = string
        })
      )
    })

    pubsub = object({
      topics = map(
        object({
          desc             = string
          messageRetention = string
        })
      )
    })

    monitoring = object({
      notificationChannels = map(
        object({
          name = string
          desc = string
        })
      )
      alertPolicies = map(
        object({
          name      = string
          condition = object({
            name         = string
            duration     = string
            comparison   = string
            aggregations = object({
              alignmentPeriod  = string
              perSeriesAligner = string
            })
            trigger = object({
              count = number
            })
          })
        })
      )
    })
  })
}
