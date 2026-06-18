# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/cache_file_for_range_read_true_test.go

Purpose: Verifies that range reads can populate the file cache when range-read caching is enabled, including RAM-cache variants.

Important APIs/types/functions: `cacheFileForRangeReadTrueTest` stores flags, clients, base test name, and RAM-cache option. `TestRangeReadsWithCacheHit` uses `readChunkAndValidateObjectContentsFromGCS`, structured read logs, job logs, `operations.RetryUntil`, cache file validation, and cache-size validation.

Control flow: the test creates an 8 MiB file, performs an initial random read at offset 5000 and expects cache miss, waits until a background file-cache job has downloaded through the full file size, then performs a second range read at offset 1000 and expects a cache hit. It then validates cached content and capacity.

State/persistence: Cache dir is cleared per test, optionally placed under `/dev/shm`. Background download job state is inferred from logs and cached file contents.

Dependencies/integration: Uses read-cache shared constants/helpers, structured read/job log parser, and setup flag sets.

Risks/test signals: Determinism depends on retrying until async job logs show sufficient offset. Passing signals range-read cache admission, background fill, and later range cache hits work.
