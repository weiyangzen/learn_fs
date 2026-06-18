# sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/constants.py

## Purpose

Centralizes BigQuery project, dataset, and table IDs for gcsfuse perfmetrics scripts.

## Important APIs, Types, and Functions

Exports string constants: `PROJECT_ID`, `DATASET_ID`, `CONFIGURATION_TABLE_ID`, `FIO_TABLE_ID`, `VM_TABLE_ID`, and `LS_TABLE_ID`.

## Control Flow

No runtime flow beyond import. Other modules use the constants to build clients, SQL strings, table references, and upload targets.

## State and Persistence Behavior

Static configuration only. The constants determine where other scripts create and mutate BigQuery resources.

## Dependencies and Integration Points

Imported by `experiments_gcsfuse_bq.py`, `get_experiments_config.py`, `setup.py`, and tests. Values must match BigQuery resources, IAM permissions, and dashboard expectations.

## Risks and Edge Cases

Hard-coded project/dataset values make local or staging runs target production-like resources unless code is changed. Table renames here require coordinated schema and dashboard migration.

## Test Signals

Successful setup/upload jobs against the configured dataset and absence of BigQuery not-found/permission errors.
