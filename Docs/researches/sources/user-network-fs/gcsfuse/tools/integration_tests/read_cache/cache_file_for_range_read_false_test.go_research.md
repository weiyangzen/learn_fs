# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/cache_file_for_range_read_false_test.go

Purpose: Validates behavior when `file-cache-cache-file-for-range-read` is false, including range-read cache misses and sequentiality after cache eviction.

Important APIs/types/functions: `cacheFileForRangeReadFalseTest` includes booleans for parallel downloads and RAM cache. `readFileBetweenOffset` records expected log metadata while reading byte ranges. Tests use file handles, `operations.OpenFile`, structured read logs, cache validation, and RAM cache path override.

Control flow: `TestRangeReadsWithCacheMiss` performs two random/range reads and expects no cached file. `TestReadIsTreatedNonSequentialAfterFileIsRemovedFromCache` partially reads two cache-capacity-sized files to evict the first, resumes reads, merges expected outcomes, validates two structured read logs, and asserts the evicted file's later chunk is non-sequential/cache-miss while the second remains sequential.

State/persistence: Cache capacity and optional `/dev/shm` cache path determine eviction behavior. Open handles are kept across partial reads, intentionally testing cache-handler lifecycle.

Dependencies/integration: Uses read-cache helpers, structured logs, setup flag builder, and testify.

Risks/test signals: Parallel downloads relax cache-hit expectations for the second file. Byte offsets use `+1` for resumed reads, so expected content merging should be interpreted as log-range validation rather than exact whole-file reconstruction. Passing signals range reads do not populate file cache unless configured and eviction resets sequentiality.
