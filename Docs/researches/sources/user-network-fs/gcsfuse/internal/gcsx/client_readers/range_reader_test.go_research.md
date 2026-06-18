## sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/range_reader_test.go

Purpose: unit test coverage for the client-side `RangeReader`, the reader that manages a reusable GCS range reader and serves `GCSReaderRequest` buffers from `NewReaderWithReadHandle`.

Important APIs and fixtures: `rangeReaderTest`, `readAt`, `mockNewReaderWithHandleCallForTestBucket`, `blockingReader`, and `countingCloser` drive mocked bucket calls and reader lifecycle assertions. The tests instantiate `NewRangeReader` with noop metrics/tracing and sometimes a filesystem config controlling interrupt propagation.

Control flow and state behavior: tests verify constructor wiring, invariant panics for missing object/bucket/state, `destroy` closing an active reader, range request construction, short reads, EOF handling, and forced reader recreation. Misalignment tests exercise invalidation when cached reader start/limit cannot satisfy a request. Cancellation tests use a blocking reader to confirm context cancellation reaches the active read only while the read is in flight.

Dependencies and integration points: depends on `storage.TestifyMockBucket`, fake readers, `gcs.ReadObjectRequest`, `cfg.Config`, `metrics`, `tracing`, `testify/suite`, and `mock`. It is a direct behavioral signal for `client_readers/range_reader.go`.

Risks and test signals: the suite is strongest around reader reuse, bounds, close behavior, and cancellation. It does not hit real GCS; any transport-specific behavior, metrics labels, or tracing payloads are indirectly checked through fake/mocked readers.
