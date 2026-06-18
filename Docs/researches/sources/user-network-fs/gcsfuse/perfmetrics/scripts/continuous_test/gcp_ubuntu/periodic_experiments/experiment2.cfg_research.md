## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiment2.cfg

Purpose: Kokoro config for periodic experiment slot 2.

APIs and integration: Sets `EXPERIMENT_NUMBER=2`, archives slot-specific gcsfuse and FIO artifacts, and dispatches to the shared periodic build script.

Control flow and state: Slot selection is performed by `jq -s ".[$EXPERIMENT_NUMBER-1]"` after date filtering.

Dependencies and risks: The job is coupled to active configuration order rather than a stable config name. Artifact regexes must match the build script's numbered log naming.

Test signals: Presence of slot-2 logs and FIO JSON is the main signal.
