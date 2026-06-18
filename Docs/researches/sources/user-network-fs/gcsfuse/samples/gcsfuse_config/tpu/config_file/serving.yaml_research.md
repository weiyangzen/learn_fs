<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/serving.yaml -->
# sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/serving.yaml

Purpose: TPU serving gcsfuse config optimized for model artifact reads with RAM disk file cache.

Important APIs, types, and functions: Declarative options enable implicit directories, `/tmp` cache dir, indefinite metadata cache, disabled negative cache, unlimited stat cache, unlimited file cache, whole-file cache for range reads, and parallel downloads.

Control flow: gcsfuse applies cache and metadata options at mount time. There is no write path configuration.

State and persistence behavior: File cache is placed under `/tmp`, expected to be RAM disk backed on TPU samples, with no size limit. Metadata cache remains valid indefinitely.

Dependencies and integration points: Corresponds to TPU serving GKE CSI templates using `gke-gcsfuse-cache` as memory-backed `emptyDir`.

Risks and test signals: Unlimited RAM-backed cache may evict or OOM workloads. Indefinite metadata cache can serve stale metadata after model updates. Serving tests should validate full-file caching and parallel download performance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/serving.yaml -->
