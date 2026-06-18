<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/mount_gcsfuse.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/mount_gcsfuse.sh

## Purpose
Mounts the read-cache benchmark bucket with generated config and optional debug logging.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
Parses flags for cache size, bucket, cache dir, range-read caching, metadata cache size, and logging; unmounts a stale mount, sleeps, generates config, and runs gcsfuse with stackdriver export.

## State And Persistence Behavior
Uses `$WORKING_DIR`, creates `$WORKING_DIR/gcs`, writes config and log files, and may unmount existing FUSE mounts.

## Dependencies
Depends on gcsfuse, mountpoint, umount, ps/grep/awk, and `generate_yml_config.sh`.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Uses unquoted variables in several places; process-id detection by grep is heuristic; the stale-unmount sleep documents a real cache-race mitigation.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/mount_gcsfuse.sh -->
