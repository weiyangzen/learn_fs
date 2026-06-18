# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/range_read_test.go

Purpose: Tests cache hit behavior for range reads within an already downloaded chunk and beyond the initial chunk after background download completion.

Important APIs/types/functions: `rangeReadTest` tracks whether parallel downloads are enabled. `TestRangeReadsWithinReadChunkSize` validates second read within an 8 MiB download window. `TestRangeReadsBeyondReadChunkSizeWithFileCached` waits for background job completion before reading at 10 MiB. `runTests` expands flag sets.

Control flow: the within-chunk test skips when parallel downloads are enabled, then reads offset 0 and 4 MiB and expects miss then hit. The beyond-chunk test reads at 0, polls job logs until offset reaches the large file size, then reads at 10 MiB and expects hit, cache file presence, and capacity compliance.

State/persistence: Cache directory stores a 15 MiB file. Background job progress is monitored through structured job logs.

Dependencies/integration: Uses read-cache helpers, setup/client/operations utilities, structured logs, and testify suite.

Risks/test signals: Async job polling is required for deterministic hits beyond the first chunk. Passing signals background cache fill can satisfy later random reads outside the initially requested range.
