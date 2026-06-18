<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/gcs_reader_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/gcs_reader_test.go

Purpose: unit tests for `GCSReader` selection, range-reader reuse, read classification, cancellation, inactive timeout wrapping, rapid-bucket MRD behavior, short-read retry, and parallel random reads.

Important APIs/types/functions: suite `gcsReaderTest`; helper `readAt`; constant `sequentialReadSizeInMb`; tests `Test_NewGCSReader`, `Test_ReadAt_InvalidOffset`, `Test_ReadAt_ExistingReaderLimitIsLessThanRequestedDataSize`, `Test_ReadAt_ExistingReaderLimitIsLessThanRequestedObjectSize`, `Test_ReadAt_ExistingReaderIsFine`, `Test_ExistingReader_WrongOffset`, `Test_ReadAt_PropagatesCancellation`, `Test_ReadAt_WithAndWithoutReadConfig`, `Test_ReadAt_ValidateZonalRandomReads`, `Test_ReadAt_ShortReadRetry`, and `Test_ReadAt_ParallelRandomReads`.

Control flow: tests configure a mock bucket, fake readers or fake MRD downloaders, and a read classifier. They call `GCSReader.ReadAt` through a helper that records read info and then assert buffer contents, reader state, expected next offset, mock calls, cancellation effects, and MRD behavior.

State and persistence behavior: all object data is in fake readers/downloaders. In-memory state under test includes `RangeReader.reader/start/limit/readHandle`, `ReadTypeClassifier`, `MultiRangeReader.mrdWrapper`, and cancellation callbacks.

Dependencies and integration points: uses `storage.TestifyMockBucket`, fake storage readers/downloaders, `gcsx.NewMultiRangeDownloaderWrapper`, cfg read options, metrics/tracing noops, and testify suite/mock.

Risks: several tests reset setup inside subtests and manually manipulate internal fields, so they are tightly coupled to implementation. Parallel random read test validates data but can hide races unless run with the Go race detector.

Test signals: proves correct EOF/invalid-offset behavior, reader reopening with read handles, preserving active range reader for partial reads, context cancellation propagation, inactive timeout reader construction, zonal random MRD selection with correct classifier updates, rapid short-read retry, and safe parallel MRD reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/gcs_reader_test.go -->
