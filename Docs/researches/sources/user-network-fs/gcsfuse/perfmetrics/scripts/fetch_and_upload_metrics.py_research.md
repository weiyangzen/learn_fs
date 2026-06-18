## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fetch_and_upload_metrics.py

Purpose: Coordinates parsing FIO JSON, optional upload to Google Sheets/BigQuery, waits for VM metrics availability, then fetches VM metrics for each FIO job and optionally uploads them.

APIs and control flow: `_parse_arguments` accepts FIO output path, `--upload_gs`, `--upload_bq`, `--config_id`, `--start_time_build`, and `--spreadsheet_id`. Main creates `FioMetrics`, parses jobs, formats upload rows, optionally writes FIO metrics, validates BigQuery args, sleeps 360 seconds, prints per-job time windows, fetches VM metrics with `VmMetrics.fetch_metrics(INSTANCE, PERIOD_SEC, rw)`, and uploads VM rows.

State and persistence: Reads FIO JSON, sleeps, writes to Sheets/BigQuery if flags are set. Uses host name as VM instance identity.

Dependencies and risks: Imports `fio`, `vm_metrics`, `gsheet`, and BigQuery modules. `_parse_arguments(argv)` ignores its parameter and always uses `sys.argv`. BigQuery validation is duplicated. Long fixed sleep slows tests and operations.

Test signals: No test file in this subset; integration signal is successful uploads or printed metrics.
