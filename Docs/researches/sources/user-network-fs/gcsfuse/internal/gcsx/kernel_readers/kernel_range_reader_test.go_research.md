## sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_range_reader_test.go

Purpose: unit tests for `KernelRangeReader` standard/regional bucket behavior.

Important APIs and fixtures: `KernelRangeReaderTest`, `mockStorageReader` implementing `ReadHandle`, mock bucket expectations, and `KernelRangeReaderInstance` setup.

Control flow and behavior covered: constructor field wiring, reader name, successful read into buffer, EOF when offset equals/over object size, partial reads capped to object size, error wrapping when creating the storage reader fails, and nil object error when the instance has no current object.

State/persistence signals: tests validate that current object size controls range limits and that a fresh storage reader is requested per read. They do not mutate the instance concurrently.

Dependencies/integration: uses `storage.TestifyMockBucket`, fake `io.NopCloser` readers, noop metrics, `testify/suite`, and GCS request types.

Risks/test signals: it confirms behavior at API boundaries but does not assert the exact request matcher for every range field in all tests. It also does not cover close errors or invariant panics.
