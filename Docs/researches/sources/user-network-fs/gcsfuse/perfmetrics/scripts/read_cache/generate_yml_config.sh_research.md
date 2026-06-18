<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/generate_yml_config.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/generate_yml_config.sh

## Purpose
Generates a GCSFuse read-cache `config.yml` from environment variables.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
Writes write, logging, cache-dir, file-cache, and metadata-cache settings with defaults for cache directory, max size, and range-read caching.

## State And Persistence Behavior
Overwrites `config.yml` in the current directory.

## Dependencies
Depends on environment variables such as `TTL_SECS` and `STAT_CACHE_MAX_SIZE_MB` being present.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Unset required env vars can produce invalid config because `set -e` does not guard here-doc expansion for missing values without `set -u`.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/generate_yml_config.sh -->
