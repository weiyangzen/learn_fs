# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/job_chunk_test.go

Purpose: Validates file-cache download job chunk sizing for single-file and concurrent multi-file reads, both with and without parallel downloads.

Important APIs/types/functions: constant `cacheSizeMB`; `jobChunkTest` stores chunk size expectation. `TestJobChunkSizeForSingleFileReads` and `TestJobChunkSizeForMultipleFileReads` use `setupFileInTestDir`, `readFileAndValidateCacheWithGCS`, `read_logs.GetJobLogsSortedByTimestamp`, `sync.WaitGroup`, and offset-difference assertions.

Control flow: single-file test reads a 16 MiB file, then checks job log bucket/object identity, monotonic increasing offsets, offsets advancing by multiples of expected chunk size, and final offset equal to file size. Multi-file test reads two files concurrently, accounts for nondeterministic log order by swapping expected outcomes, then applies the same offset checks to both jobs.

State/persistence: Download progress is inferred entirely from structured job logs. Cache dir is cleared per test.

Dependencies/integration: Uses internal cache `util.MiB`, read-cache helpers, setup flag sets with 8 MiB or 4 MiB chunk expectations, and structured logs.

Risks/test signals: Uses `setup.LogFile()` rather than `testEnv.cfg.LogFile`; this assumes setup global log file was updated consistently. Passing signals configured chunk sizes are reflected in download job telemetry.
