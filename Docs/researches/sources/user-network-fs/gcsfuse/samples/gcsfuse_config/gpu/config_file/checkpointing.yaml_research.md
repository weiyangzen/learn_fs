<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/checkpointing.yaml -->
# sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/checkpointing.yaml

Purpose: Example gcsfuse config for GPU checkpointing workloads that read and write model checkpoints through a mounted GCS bucket.

Important APIs, types, and functions: This is declarative YAML for gcsfuse configuration. It enables `implicit-dirs`, uses `/tmp` as `cache-dir`, configures `metadata-cache` with `negative-ttl-secs: 0`, `ttl-secs: -1`, and unlimited stat cache, enables unlimited `file-cache`, whole-file caching for range reads, parallel downloads, and `write.enable-streaming-writes`.

Control flow: At mount startup, gcsfuse reads these options and applies metadata caching, file caching, and streaming write behavior. There is no executable control flow in the file.

State and persistence behavior: File content cache is stored under `/tmp`; comments indicate GPU deployments expect local SSD backing. Metadata entries and file cache can grow without explicit size limit because both max sizes are `-1`. Streaming writes alter write path behavior for checkpoint output.

Dependencies and integration points: Intended for gcsfuse config-file consumption and to correspond to GKE CSI checkpointing PV mount options. It assumes workloads can tolerate indefinite metadata cache TTL and that `/tmp` has enough capacity for checkpoint cache pressure.

Risks and test signals: Unlimited metadata and file caches can consume local disk. `ttl-secs: -1` can expose stale metadata when other writers mutate the bucket. The checkpointing-specific signal is streaming writes enabled, unlike serving/training configs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/checkpointing.yaml -->
