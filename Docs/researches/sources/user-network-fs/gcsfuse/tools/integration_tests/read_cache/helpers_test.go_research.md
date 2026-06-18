# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/helpers_test.go

Purpose: Central helper library for read-cache tests, covering expected log metadata, mounted reads, GCS content validation, cache path lookup, cache file validation, remounting, mutation, capacity checks, sparse allocation checks, chunk download validation, and content verification.

Important APIs/types/functions: `Expected` stores log validation data and served content. `readFileAndGetExpectedOutcome`, `validate`, `getCachedFilePath`, `validateFileSizeInCacheDirectory`, `validateFileInCacheDirectory`, `validateFileIsNotCached`, `validateFileIsCached`, `remountGCSFuse`, `readFileAndValidateCacheWithGCS`, `readChunkAndValidateObjectContentsFromGCS`, `readFileAndValidateFileIsNotCached`, `modifyFile`, `validateCacheSizeWithinLimit`, `setupFileInTestDir`, `runTestsOnlyForDynamicMount`, `validateAllocatedFileSize`, `validateDownloads`, and `validateContent` are reused across suites.

Control flow: helpers usually perform a mounted read, capture timestamps, compare served bytes against GCS via CRC or chunk validation, then inspect cache files and structured logs. Retry loops handle asynchronous cache materialization and CRC availability.

State/persistence: Computes cache paths from cache dir, bucket name, test directory basename, and file name. It mutates object content directly through GCS for invalidation tests and remounts gcsfuse by unmounting root and mounting with saved config.

Dependencies/integration: Uses Cloud Storage, internal cache range types, read log parser, setup/client/operations utilities, syscalls, CRC helpers, and testify.

Risks/test signals: Many suites depend on exact structured-log ordering and cache path layout. Helpers deliberately validate both data correctness and telemetry, making failures high-signal for cache implementation regressions.
