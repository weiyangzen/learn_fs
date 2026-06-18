<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/training.yaml -->
# sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/training.yaml

Purpose: Example gcsfuse config for GPU training workloads where metadata caching is recommended and file content caching is optional depending on dataset size.

Important APIs, types, and functions: Active options enable `implicit-dirs` and metadata cache settings (`negative-ttl-secs: 0`, `ttl-secs: -1`, unlimited stat cache). File cache settings are commented out with a `<DATASET_SIZE>` placeholder.

Control flow: At mount time, gcsfuse applies only implicit directory and metadata cache options. File content cache is disabled unless the user uncommentes and sizes the `cache-dir`/`file-cache` block.

State and persistence behavior: Active state is limited to metadata cache, which may persist indefinitely for the mount lifetime. Optional file cache would store data under `/tmp` if enabled.

Dependencies and integration points: Intended for training jobs using gcsfuse config files and GPU local SSD `/tmp` when optional cache is enabled. It mirrors the training PV template where file cache mount options are commented out.

Risks and test signals: Indefinite metadata cache can hide external dataset changes. Commented file cache block avoids default disk blow-up but requires user sizing; bad substitution of `<DATASET_SIZE>` would break config if copied literally.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/training.yaml -->
