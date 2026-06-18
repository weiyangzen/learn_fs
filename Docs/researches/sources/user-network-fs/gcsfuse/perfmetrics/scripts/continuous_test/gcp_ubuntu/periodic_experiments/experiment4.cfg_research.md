## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiment4.cfg

Purpose: Kokoro config for periodic experiment slot 4.

APIs and integration: Sets `EXPERIMENT_NUMBER=4`, archives the fourth numbered logs/FIO output, and runs `periodic_experiments/build.sh`.

Control flow and state: This config has no logic beyond env var and artifact definitions.

Dependencies and risks: Requires at least four active configs in `experiments_configuration.json`. The current config set has exactly four entries, so adding expiry or reordering affects the job.

Test signals: Slot-4 gcsfuse log, list log, and FIO JSON are expected outputs.
