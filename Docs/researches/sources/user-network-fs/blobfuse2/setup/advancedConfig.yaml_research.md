<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/advancedConfig.yaml -->
# sources/user-network-fs/blobfuse2/setup/advancedConfig.yaml

## Purpose
Comprehensive annotated Blobfuse2 configuration reference showing daemon, logging, pipeline, cache, storage, mount-all, and health-monitor options.

## Important APIs, Types, and Functions
Major sections include top-level mount/daemon flags, `logging`, `components`, `libfuse`, `entry_cache`, `xload`, `block_cache`, `file_cache`, `attr_cache`, `loopbackfs`, `azstorage`, `mountall`, and `health_monitor`. The file documents defaults, accepted values, production cautions, and interaction notes such as block cache versus file cache exclusivity.

## Control Flow and State
The file is a human-editable template, not a valid ready-to-run config because many values are placeholders with inline explanatory text. When converted into real YAML values, it controls pipeline composition, cache persistence paths/sizes, auth mode, retry behavior, ACL behavior, rate caps, and monitor output.

## Dependencies and Integration Points
Consumed conceptually by Blobfuse2 users and referenced by scripts/docs. It mirrors config fields parsed across Blobfuse2 components and setup rsyslog/logrotate files.

## Risks and Edge Cases
Copying it directly without removing explanatory placeholders will fail YAML/config parsing. Some options are production-sensitive: `loopbackfs` is testing-only, `log_debug` can expose detailed logs, cache paths need capacity, and `allow-other` also requires `/etc/fuse.conf` changes. The comments mention `sdk-trace` removal and stream/direct behavior constraints.

## Test Signals
This file is documentation. Signal comes from consistency with parser-supported config keys and from users successfully deriving working configs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/setup/advancedConfig.yaml -->
