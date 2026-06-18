# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/GrpcOutputStream.java

Purpose: provides the shared `OutputStream` to gRPC stream adapter used by both pull download responses and push upload requests.

Important APIs and functions: `write(int)` and `write(byte[], int, int)` buffer data in a protobuf `ByteString.Output` until `bufferSize` is reached. `close()` flushes remaining data with `eof=true`, logs total bytes, calls `onCompleted`, and closes the buffer once. `flushBuffer` waits for readiness, converts the buffer to a `ByteString`, calls subclass `sendPart`, increments `writtenBytes`, and resets the buffer. `waitUntilReady` polls `CallStreamObserver.isReady()` with 10 ms sleeps up to 30,000 tries.

Control flow and state: `closed` is an `AtomicBoolean`; writes after close fail via Guava `Preconditions`. Write exceptions call `streamObserver.onError(ex)` but do not rethrow for the single-byte path. Subclasses supply message construction while this class owns byte counting and backpressure.

Dependencies and integration: parent for `CopyContainerResponseStream` and `SendContainerOutputStream`.

Risks and test signals: polling backpressure can block executor threads for up to five minutes. Tests should cover write bounds, chunk splitting, close idempotence, interruption, readiness timeout, observer errors, and exact `writtenBytes` offsets in subclass messages.
