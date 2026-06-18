# sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/experiments_gcsfuse_bq_test.py

## Purpose

Unit tests for `ExperimentsGCSFuseBQ` that validate BigQuery helper control flow without live BigQuery.

## Important APIs, Types, and Functions

Uses `unittest`, `uuid`, `patch`, `MagicMock`, `Table`, local constants, and `ExperimentsGCSFuseBQ`. `setUp` patches the BigQuery module and injects a mock client. Tests cover `_check_if_config_valid`, `_execute_query`, `_insert_rows`, `setup_dataset_and_tables`, `get_experiment_configuration_id`, and `upload_metrics_to_table`.

## Control Flow

Tests configure mock query jobs/tables/client methods, call the target helper, and assert return values, exceptions, call counts, insert rows, and cleanup `DELETE` query shape.

## State and Persistence Behavior

No real persistence. BigQuery state changes are represented by mock calls to `create_dataset`, `query`, `get_table`, and `insert_rows`.

## Dependencies and Integration Points

Designed to run from `perfmetrics/scripts` as `python3 -m bigquery.experiments_gcsfuse_bq_test`. Mirrors the implementation's current private methods and SQL formatting behavior.

## Risks and Edge Cases

Mocks may not fully represent BigQuery client behavior. One insert-new configuration test passes arguments in an order that exposes fragility around function signature and row order. Does not cover SQL escaping, live IAM/schema issues, or the optional CLI config-file argument.

## Test Signals

Failures in exception text, cleanup query text, setup query count, duplicate/mismatch config handling, or invalid upload handling are important regression signals.
