## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/build.sh

Purpose: Kokoro build script for parameterized periodic gcsfuse performance experiments.

APIs and control flow: Installs `git` and `jq`, loads `experiments_configuration.json`, filters configurations with `end_date >= current_date`, selects by one-based `EXPERIMENT_NUMBER`, optionally writes `config_flags.yml` from `config_file_flags_as_json`, builds gcsfuse for the configured branch, installs BigQuery requirements, registers/fetches a `CONFIG_ID`, conditionally enables BigQuery upload flags for Kokoro job types, runs FIO load tests through `run_load_test_and_fetch_metrics.sh`, then runs list benchmarks via `ls_metrics/run_ls_benchmark.sh`.

State and persistence: Writes transient config files under `KOKORO_ARTIFACTS_DIR`, installs packages and Python user packages, builds/install gcsfuse, writes log files and metrics, and uploads to BigQuery when enabled.

Dependencies and risks: Depends on `EXPERIMENT_NUMBER`, Kokoro env vars, jq, pip requirements, BigQuery modules, bucket names, and shell quoting. Use of `eval` around the Python config command and unquoted JSON variables increases quoting risk.

Test signals: Logs, FIO output JSON, list logs, and BigQuery rows indicate successful execution.
