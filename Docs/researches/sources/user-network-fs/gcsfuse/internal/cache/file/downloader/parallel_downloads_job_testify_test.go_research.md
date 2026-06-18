<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job_testify_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job_testify_test.go

## Purpose
This testify suite verifies parallel download read-handle behavior with mocked GCS readers. It complements content-based parallel tests by asserting how `NewReaderWithReadHandle` is called across chunks and workers.

## Important fixtures and APIs
`ParallelDownloaderJobTestifyTest` embeds `JobTestifyTest` and configures parallel downloads with three workers, 3 MiB chunks, CRC enabled, and 4 MiB write buffer. The main test creates four expected ranges for a 10 MiB object and assigns fake readers with a shared opaque handle.

## Control flow and state behavior
The test sets mock expectations for four ranged `NewReaderWithReadHandle` calls. The first chunk must use a nil read handle, middle chunks may use nil or propagated handles because worker scheduling is nondeterministic, and the fourth chunk is expected to use a non-nil handle. Counters protected by a mutex record total call count and nil-handle calls, allowing nondeterministic worker ordering while still bounding expected behavior. After download, the test verifies subscriber notification, local file content, and file-info cache.

## Dependencies and integration points
The suite uses `storage.TestifyMockBucket`, fake readers, testify mock matchers, cache utilities, and the shared helper functions from `test_util.go`. It directly validates the contract between parallel workers and the GCS read-handle optimization.

## Risks and edge cases
Because parallel scheduling is nondeterministic, the test intentionally allows a range of nil-handle counts. The expectation that the last chunk has a non-nil read handle can be sensitive to worker assignment. The mock content is partitioned by chunk and assumes exact chunk ranges, so changes to range sizing or chunk scheduling require coordinated test updates.

## Test signals
The file signals that parallel downloads issue one GCS reader per chunk, propagate handles within workers, notify subscribers, reconstruct the full file, and update the file-info cache despite concurrent reader calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job_testify_test.go -->
