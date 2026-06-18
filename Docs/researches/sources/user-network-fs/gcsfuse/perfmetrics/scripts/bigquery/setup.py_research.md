# sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/setup.py

## Purpose

Executable wrapper for initializing the BigQuery dataset and perfmetrics tables.

## Important APIs, Types, and Functions

Imports local `experiments_gcsfuse_bq` and `constants`; main constructs `ExperimentsGCSFuseBQ` and calls `setup_dataset_and_tables()`.

## Control Flow

Linear wrapper. All schema creation and BigQuery query execution are delegated to `experiments_gcsfuse_bq.py`.

## State and Persistence Behavior

Can create the `performance_metrics` dataset and the configuration, fio, VM, and list metric tables. Writes no local files.

## Dependencies and Integration Points

Requires BigQuery credentials/API enablement, hard-coded constants, and the schema SQL in the helper class. Intended usage is `python3 -m bigquery.setup`.

## Risks and Edge Cases

Despite the filename, this is not a setuptools packaging script. It has no project/dataset CLI override. Existing tables are not migrated because setup uses `CREATE TABLE IF NOT EXISTS`.

## Test Signals

Mocked call to `setup_dataset_and_tables` and live idempotent BigQuery setup with no schema errors.
