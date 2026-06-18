<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job_testify_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job_testify_test.go

## Purpose
This testify suite adds mock-based downloader tests, primarily to verify exact GCS reader requests and read-handle propagation that are hard to assert with the fake storage suite. It is the migration target for new `Job` tests.

## Important fixtures and APIs
`JobTestifyTest` embeds `suite.Suite` and owns a context, default file-cache config, `Job`, object metadata, LRU cache, file spec, and `storage.TestifyMockBucket`. `initReadCacheTestifyTest` constructs a `Job` around the mock bucket, creates a file-info cache entry, and uses disk block size for job construction.

## Control flow and state behavior
`Test_downloadObjectToFile_WithReadHandle` creates a 10 MiB object, configures sequential read size to 5 MiB, and sets mocked `NewReaderWithReadHandle` expectations for two ranges. The first range uses a nil read handle; the fake reader returns an opaque handle; the second range must pass that handle back. The test subscribes to the full object offset, invokes `downloadObjectToFile`, and validates subscriber notification, file content, and file-info cache progress.

## Dependencies and integration points
This file depends on testify suite/assert/mock, `storage.TestifyMockBucket`, fake readers, cache data/LRU utilities, diskutil, metrics/tracing no-ops, and `semaphore.NewWeighted`. It complements fake-storage tests by asserting request structs, not just final file content.

## Risks and edge cases
The mock returns the same fake reader object for both ranges; because the reader wraps a string reader, this works for the test expectation but could hide independent-reader lifecycle details. The file path under `$HOME/cache/dir` is shared with other downloader tests. Only the sequential read-handle path is covered here; error propagation and cancellation remain in legacy tests.

## Test signals
The main signal is that sequential downloads reuse GCS read handles across range requests, request exact byte ranges, notify offset subscribers, write complete local content, and update file-info cache to at least object size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job_testify_test.go -->
