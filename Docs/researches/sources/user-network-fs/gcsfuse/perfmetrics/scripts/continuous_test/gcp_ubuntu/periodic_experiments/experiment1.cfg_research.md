## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiment1.cfg

Purpose: Kokoro config for periodic experiment slot 1.

APIs and integration: Sets `EXPERIMENT_NUMBER=1`, collects numbered FIO and list logs, and invokes `periodic_experiments/build.sh`.

Control flow and state: The build script uses the environment value to select the first currently enabled item from `experiments_configuration.json`.

Dependencies and risks: The one-based slot is order-dependent after filtering expired configurations. Reordering active configs changes what experiment this Kokoro job runs.

Test signals: Numbered artifacts `gcsfuse-logs1.txt`, `gcsfuse-list-logs1.txt`, and `fio-output1.json` should be produced.
