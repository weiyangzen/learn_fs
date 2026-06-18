## sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/config-flat.json

Purpose: Input configuration for flat-bucket HNS rename-folder benchmark data generation.

APIs and structure: Defines bucket/name `hns-rename-benchmark-flat`, three top-level folders containing 1k, 5k, and 10k one-kilobyte files, and a nested folder group with ten second-level folders of 1k files each.

Control flow and state: Consumed by `generate_folders_and_files.py`, which verifies or creates the described GCS object structure.

Dependencies and risks: `num_folders` must match `folder_structure` lengths or validation fails. File sizes use the two-character `1kb` format expected by the generator.

Test signals: The generator's structure comparison should find exactly the configured folder and file counts.
