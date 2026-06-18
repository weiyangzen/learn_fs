# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/chunk_cache_test.go

Purpose: Provides broad coverage for experimental chunk cache: random reads, full sequential reads, reuse of cached chunks, reads spanning chunks, concurrent deduplication, deleted-object fallback errors, and sparse-file allocation.

Important APIs/types/functions: `chunkCacheTest` uses common setup/teardown. Tests use `readChunkAndValidateObjectContentsFromGCS`, `readFileAndValidateCacheWithGCS`, `validateDownloads`, `validateAllocatedFileSize`, `operations.ReadChunkFromFile`, direct GCS deletion, structured job/read logs, and `sync.WaitGroup`.

Control flow: individual tests create files sized around 10 MiB chunk boundaries, perform reads at strategic offsets, assert read-log sequential/cache-hit flags, and compare chunk download ranges. Concurrent dedup launches eight goroutines reading the same chunk and expects one download. Deleted-file test reads one chunk, deletes the source object, then expects second chunk read to return ESTALE and log fallback messages.

State/persistence: Chunk cache stores sparse files under cache dir; tests inspect both logical content and allocated block size. Deletion test intentionally desynchronizes mounted metadata from backend object existence.

Dependencies/integration: Uses internal cache data/util packages, client operations, read logs, and filesystem syscalls.

Risks/test signals: Some tests assume a single job log contains all downloads. The deleted-file test checks log text substrings. Passing signals chunk-cache correctness, deduplication, sparse allocation, and stale-source error handling.
