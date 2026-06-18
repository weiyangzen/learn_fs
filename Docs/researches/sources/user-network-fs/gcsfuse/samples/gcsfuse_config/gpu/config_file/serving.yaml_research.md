<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/serving.yaml -->
# sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/serving.yaml

Purpose: Example gcsfuse config for GPU serving workloads optimized for cached model artifact reads.

Important APIs, types, and functions: Declarative gcsfuse options enable `implicit-dirs`, `/tmp` cache directory, indefinite positive metadata cache, disabled negative lookup cache, unlimited stat cache, unlimited file cache, whole-file cache on range read, and parallel downloads.

Control flow: The serving mount reads these options at startup and serves later file reads through metadata and file caches. No write-specific section is present.

State and persistence behavior: File cache and metadata cache can persist for the mount lifetime with no configured size cap. Serving is read-heavy, so the config omits streaming writes and prioritizes parallel download/cache behavior.

Dependencies and integration points: Integrates with gcsfuse config-file mounting and GPU local SSD `/tmp` cache assumptions. It aligns with GKE serving PV options and serving pod examples that mount a cache volume.

Risks and test signals: Unlimited file cache can exhaust `/tmp`; indefinite metadata TTL can become stale if model objects change under the mount. Test signals should verify that read cache and parallel download behavior are effective for serving artifacts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gcsfuse_config/gpu/config_file/serving.yaml -->
