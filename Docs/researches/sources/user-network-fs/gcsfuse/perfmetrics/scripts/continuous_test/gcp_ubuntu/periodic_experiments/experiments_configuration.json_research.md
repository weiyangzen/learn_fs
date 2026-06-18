## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiments_configuration.json

Purpose: Data contract for periodic experiment variants consumed by `build.sh`.

APIs and structure: Contains `experiment_configuration`, an ordered array of config objects with `config_name`, `gcsfuse_flags`, `branch`, `end_date`, and optional `config_file_flags_as_json`. The current entries compare master defaults, range-read cache enabled, range-read cache disabled, and gRPC client protocol.

Control flow and state: The shell script filters entries by `end_date`, then selects by `EXPERIMENT_NUMBER` index. Optional config-file flags are serialized into a temporary config file and passed via `--config-file`.

Dependencies and risks: Date strings are compared by jq as strings, so format consistency matters. The file's array order is an external scheduling API for numbered Kokoro jobs.

Test signals: A valid config should produce a BigQuery config id through `bigquery.get_experiments_config`.
