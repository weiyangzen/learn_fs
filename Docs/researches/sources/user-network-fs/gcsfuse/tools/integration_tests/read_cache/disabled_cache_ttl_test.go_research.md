# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/disabled_cache_ttl_test.go

Purpose: Validates that disabling stat/cache TTL causes reads after backend object updates to miss cache and fetch fresh content, while subsequent reads can hit the refreshed cache.

Important APIs/types/functions: `disabledCacheTTLTest` follows common suite lifecycle. `TestReadAfterObjectUpdateIsCacheMiss` uses `setupFileInTestDir`, `readFileAndValidateCacheWithGCS`, `modifyFile`, structured logs, and `validate`.

Control flow: the test creates a file, reads it once to populate cache, modifies the object directly through the storage client, reads immediately again expecting a miss and smaller updated file, then reads a third time expecting a hit for the updated object. It validates all three structured read logs.

State/persistence: Direct GCS mutation changes object generation outside gcsfuse. Cache directory is cleared before test and then refreshed after miss.

Dependencies/integration: Uses setup flag variants with `--stat-cache-ttl=0s`, read-cache helpers, storage client, and structured log parser.

Risks/test signals: Assumes object update is immediately visible with stat TTL zero. Passing signals stale cached file contents are invalidated by object generation/metadata changes.
