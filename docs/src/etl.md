# ETL: Data pipeline

The ETL process is wrapped into 3 workflows:

* Main workflow (`{{ pattern("workflows.etl")}}`) which list all the subjects (currencies) and runs the `{{ pattern("workflows.wrapper")}}` workflow for each of them
* Wrapper workflow (`{{ pattern("workflows.wrapper")}}`) which is responsible for running the `{{ pattern("workflows.subject")}}` ensuring the logging, tracing and error handling (notification on mattermost)
* Core workflow (`{{ pattern("workflows.subject")}}`) which is responsible for sourcing data from Exchange Rates API to BigQuery for the given subject (currency)

Following image shows the data pipeline (Core Workflow: `{{ pattern("workflows.subject")}}`) used for running the ETL. This process is followed for each subject (currency pair) separately.

![Infra](./static/drawings/etl.flow.drawio)