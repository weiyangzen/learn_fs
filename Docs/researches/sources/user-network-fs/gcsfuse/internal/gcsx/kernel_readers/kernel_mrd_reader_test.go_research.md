## sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_mrd_reader_test.go

Purpose: validates `KernelMRDReader` and its short-read retry logic over fake MRD instances.

Important APIs and fixtures: `KernelMRDReaderTest`, configured `MrdInstance`, fake multi-range downloaders, mock bucket calls, and table tests for `isShortRead`.

Control flow and behavior covered: constructor fields, empty-buffer fast path, normal read, multiple reads reusing one MRD pool, nil instance error, short reads that should not retry, gRPC OutOfRange short reads that recreate MRD and retry remaining data, retry failures, recreation failure fallback to old MRD, destroy after use, destroy before read, and context cancellation propagation.

State/persistence signals: tests check MrdInstance refcount transitions, reuse of the same pool across multiple reads, and recreation calls through `NewMultiRangeDownloader`. Short-read tests verify final byte counts combine first attempt and retry.

Dependencies/integration: uses internal fake MRDs, `storage.TestifyMockBucket`, `cfg.Config`, noop metrics, gRPC `status.Error`, and `testify/suite`.

Risks/test signals: strong unit coverage for rapid bucket reader behavior, but not kernel read-ahead itself. Concurrent reads are not directly stressed in this file.
