<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/training.yaml -->
# sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/training.yaml

Purpose: TPU training gcsfuse config that enables metadata cache and leaves file cache as an opt-in block sized to the dataset.

Important APIs, types, and functions: Active YAML config contains `implicit-dirs: true` and metadata-cache settings for disabled negative cache, indefinite positive TTL, and unlimited stat cache. The optional `cache-dir` and `file-cache` lines are comments with `<DATASET_SIZE>`.

Control flow: Only active metadata and implicit-directory options are applied by gcsfuse unless the operator edits the commented file-cache block.

State and persistence behavior: Metadata cache persists for the mount lifetime. Optional file cache would use `/tmp` RAM disk on TPU, so it must be sized deliberately.

Dependencies and integration points: Aligns with TPU training GKE CSI samples. It is intended for workloads where the dataset may not fit safely in RAM-backed cache.

Risks and test signals: The commented `#file-cache:` line lacks a space after `#`, but remains a YAML comment. Risks include stale metadata and operator error when enabling a file cache with an unsized placeholder.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/training.yaml -->
