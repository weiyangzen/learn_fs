## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestStreamBlockInputStream.java

**Purpose:** Tests custom stream-read configuration, stream permit/request completion behavior, close failure handling, and race conditions in queue draining for `StreamBlockInputStream`.

**Important APIs/types/functions:** `testCustomStreamReadConfigIsApplied()` asserts pre-read size, response data size, and timeout fields are copied from `OzoneClientConfig`. `testReleasesStreamPermitAtBlockEof()` reads to EOF and verifies `XceiverClientGrpc.completeStreamRead()` and request observer `onCompleted()` happen once. `testCancelsRequestStreamWhenOnCompletedThrows()` and `testCloseDoesNotFailWhenOnCompletedAndCancelThrow()` verify close cleanup remains robust when observer completion/cancel throw. `testPollDoesNotDropQueuedItemWhenFutureCompletesFirst()` drives a race where `onNext` and `onCompleted` both happen before polling. `testReadDoesNotDropQueuedItemsWhenFutureIsDoneOnSecondCall()` drives multiple queued responses followed by completion and asserts all queued data is read. Helpers build standalone pipelines and mocked streaming clients/responses.

**Control flow:** The stream initializes a gRPC streaming read, queues `ReadBlock` responses through `StreamingReaderSpi`, consumes queued responses into caller buffers, and completes/cancels the request stream on EOF or close. The race tests specifically require queue draining before treating a completed future as EOF.

**State and persistence:** In-memory state includes block position, queued streaming responses, future completion state, request observer lifecycle, and stream permit state in the client. No persistence.

**Dependencies and integration points:** Depends on `XceiverClientGrpc`, `StreamingReadResponse`, `StreamingReaderSpi`, gRPC `ClientCallStreamObserver`, protobuf `ReadBlockResponseProto`, pipelines, `OzoneClientConfig`, and Mockito. Integrates with datanode streaming block read support.

**Risks:** The race tests encode current bug/regression expectations and are sensitive to internal queue/future ordering. Mocked streaming callbacks do not cover real network scheduling but reproduce the problematic synchronous ordering.

**Test signals:** High-value signal for streaming read resource cleanup and for preventing data loss/NPE when completion races with queued responses.
