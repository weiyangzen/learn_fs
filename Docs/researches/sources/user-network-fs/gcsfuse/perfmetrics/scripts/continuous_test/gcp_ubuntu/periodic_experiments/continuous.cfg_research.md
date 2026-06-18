## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/continuous.cfg

Purpose: Kokoro config for the unnumbered periodic experiment job.

APIs and integration: Collects `gcsfuse-logs.txt`, `gcsfuse-list-logs.txt`, and `fio-output.json`; invokes `periodic_experiments/build.sh`.

Control flow and state: This file provides artifact collection only and does not set `EXPERIMENT_NUMBER`. The build script therefore requires the environment to provide it or may fail under `set -e`.

Dependencies and risks: Artifact names differ from the numbered experiment configs. Risk is an unset `EXPERIMENT_NUMBER` if Kokoro does not inject it separately.

Test signals: Kokoro should archive the configured logs and FIO JSON.
