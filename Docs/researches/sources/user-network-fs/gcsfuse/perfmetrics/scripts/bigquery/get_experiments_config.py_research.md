# sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/get_experiments_config.py

## Purpose

CLI wrapper that prints a BigQuery experiment configuration ID for a given gcsfuse performance configuration, creating or updating the configuration row if needed.

## Important APIs, Types, and Functions

Defines `parse_arguments(argv)` with `--gcsfuse_flags`, optional `--config_file_flags_as_json`, `--branch`, `--end_date`, and `--config_name`. Main constructs `ExperimentsGCSFuseBQ(constants.PROJECT_ID, constants.DATASET_ID)` and calls `get_experiment_configuration_id`.

## Control Flow

Parses `sys.argv`, unwraps one-element argument lists, delegates database logic to `ExperimentsGCSFuseBQ`, and prints the returned ID.

## State and Persistence Behavior

May insert or update a row in BigQuery `experiment_configuration`. Writes no local files.

## Dependencies and Integration Points

Depends on local BigQuery helper/constants, `argparse`, and credentials for the configured project. Intended for perfmetrics shell workflows needing a stable config ID before uploads.

## Risks and Edge Cases

`parse_arguments` ignores the passed `argv` and reads `sys.argv`. `--config_file_flags_as_json` is optional but main unconditionally indexes it, so omission fails. `nargs=1` complicates direct use. Values flow to downstream interpolated SQL.

## Test Signals

Tests should cover all-argument parsing, omitted optional config JSON, injected argv behavior, and mocked helper argument order.
