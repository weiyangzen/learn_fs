# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/chunk_cache_disabled_test.go

Purpose: Ensures normal file-cache downloads are used when experimental chunk cache is explicitly disabled.

Important APIs/types/functions: `chunkCacheDisabledTest` follows the common suite pattern. `TestNormalFileCacheWithChunkCacheDisabled` creates a 10 MiB file, reads a chunk, validates structured read logs, then inspects job logs for chunk versus normal file-cache downloads.

Control flow: after setup clears logs/cache and creates a unique directory, the test performs one chunk read, validates a sequential cache miss in read logs, requires exactly one job log, asserts `ChunkCacheDownloads` is empty, and asserts normal `JobEntries` are present.

State/persistence: Cache artifacts and log entries are the primary observed state. The file is created in GCS and read through the mount.

Dependencies/integration: Uses internal cache `util.MiB`, read-cache helpers, structured logs, and setup/client/operations helpers.

Risks/test signals: It assumes exactly one job log for the read. Passing distinguishes disabled chunk-cache behavior from chunk-cache download telemetry.
