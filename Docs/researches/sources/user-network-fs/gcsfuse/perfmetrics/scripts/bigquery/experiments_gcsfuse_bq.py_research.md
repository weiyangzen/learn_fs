# sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/experiments_gcsfuse_bq.py

## Purpose

BigQuery persistence layer for gcsfuse performance experiments. It creates the perfmetrics dataset/tables, manages experiment configuration IDs, validates configurations, and uploads metric rows.

## Important APIs, Types, and Functions

Main class: `ExperimentsGCSFuseBQ(project_id, dataset_id, bq_client=None)`. Important members are `dataset_ref`, `_get_table_from_table_id`, `_execute_query`, `_check_if_config_valid`, `_delete_rows_incomplete_transaction`, `_insert_rows`, `setup_dataset_and_tables`, `get_experiment_configuration_id`, and `upload_metrics_to_table`.

## Control Flow

Setup creates a dataset, sleeps 120 seconds, then issues `CREATE TABLE IF NOT EXISTS` SQL for `experiment_configuration`, fio metrics, VM metrics, and list metrics. Configuration lookup selects by `configuration_name`, inserts a UUID for new configs, rejects duplicates, checks existing flags/branch, updates end date if different, and returns the config ID. Upload validates the config ID, prepends config/build metadata to metric rows, inserts them, and attempts cleanup on insert failure.

## State and Persistence Behavior

Persists BigQuery datasets, tables, configuration rows, and metric rows. Failed insert cleanup deletes rows for the same table, config ID, and build start time, but it is not a real transaction.

## Dependencies and Integration Points

Uses `google.cloud.bigquery`, `QueryJob`, `uuid`, `time`, and local constants. Called by setup/config CLI wrappers and perfmetrics upload workflows; tested through an injected mock BigQuery client.

## Risks and Edge Cases

SQL is built by direct string interpolation, so quotes in flags/config names/JSON can break queries or create injection risk. `end_date` uses identity comparison (`is not`) rather than equality. Existing config checks ignore `config_file_flags_as_json`. Cleanup can delete previous rows if `start_time_build` is reused. Dataset lookup relies on client default project behavior.

## Test Signals

Unit tests cover query errors, config validation, insert cleanup, setup query count, new/existing/update config flows, and invalid upload config rejection. Live signals are successful schema creation and metric row insertion.
