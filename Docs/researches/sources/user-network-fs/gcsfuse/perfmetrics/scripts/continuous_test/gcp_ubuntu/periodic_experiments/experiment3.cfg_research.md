## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiment3.cfg

Purpose: Kokoro config for periodic experiment slot 3.

APIs and integration: Sets `EXPERIMENT_NUMBER=3`, defines artifact regexes for `gcsfuse-logs3.txt`, `gcsfuse-list-logs3.txt`, and `fio-output3.json`, and invokes the shared build script.

Control flow and state: It delegates experiment choice and all benchmark execution to `build.sh`.

Dependencies and risks: Same order-coupling risk as other numbered slots. Missing or expired third configuration causes the build script to print no enabled config and exit successfully without running benchmarks.

Test signals: Slot-3 artifact collection and BigQuery upload, when enabled.
