## sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/config-hns.json

Purpose: Input configuration for HNS-bucket rename-folder benchmark data generation.

APIs and structure: Mirrors `config-flat.json` but targets bucket/name `hns-rename-benchmark-hns`. It defines identical top-level and nested folder/file counts for comparing flat versus hierarchical namespace behavior.

Control flow and state: The data generator uses it to validate existing GCS structure or recreate bucket contents.

Dependencies and risks: Because it is intentionally parallel to the flat config, drift between the two files would weaken benchmark comparability.

Test signals: Successful validation requires all configured folders and file counts to match in the HNS bucket.
