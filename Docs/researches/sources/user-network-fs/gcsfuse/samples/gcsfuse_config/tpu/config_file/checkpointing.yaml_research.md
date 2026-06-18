<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/checkpointing.yaml -->
# sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/checkpointing.yaml

Purpose: TPU checkpointing gcsfuse config equivalent to the GPU checkpointing profile, with comments noting `/tmp` is expected to be RAM disk backed on TPU.

Important APIs, types, and functions: Enables `implicit-dirs`, `/tmp` cache directory, metadata cache with disabled negative cache and indefinite positive cache, unlimited stat and file cache sizes, whole-file range-read caching, parallel downloads, and streaming writes.

Control flow: Declarative mount configuration is consumed by gcsfuse during startup; checkpoint writes use the streaming writes path.

State and persistence behavior: Uses `/tmp` for file cache, which may be RAM-backed on TPU. Unlimited cache sizing and indefinite metadata TTL persist until mount/cache cleanup.

Dependencies and integration points: Integrates with TPU workload deployments and matches the TPU checkpointing GKE CSI PV/POD examples that allocate RAM disk cache.

Risks and test signals: RAM disk exhaustion is a stronger risk for TPU than GPU local SSD. Streaming write behavior should be validated for checkpoint output; stale metadata remains a risk with `ttl-secs: -1`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/tpu/config_file/checkpointing.yaml -->
