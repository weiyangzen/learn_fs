<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMGrpcOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMGrpcOutputStream.java

## Purpose

`SCMGrpcOutputStream` adapts an `OutputStream` interface to a gRPC `StreamObserver` for streaming SCM DB checkpoint bytes as `CopyDBCheckpointResponseProto` chunks.

## Important APIs, Types, and Functions

It overrides `write(int)`, `write(byte[], int, int)`, and `close`. Private `flushBuffer` emits protobuf chunks containing cluster ID, data, EOF flag, read offset, and length.

## Control Flow

Writes append into a `ByteString.Output` buffer. When the buffer reaches the configured size, it emits a chunk with `eof=false`, increments `writtenBytes`, and resets the buffer. `close` flushes any remaining bytes with `eof=true`, logs the total, calls `onCompleted`, and closes the buffer.

## State and Persistence Behavior

State is in-memory buffer, cluster ID, buffer size, observer, and byte offset. No local persistence occurs; remote client persists received bytes.

## Dependencies and Integration Points

It integrates with `InterSCMGrpcService`, inter-SCM protobufs, and gRPC stream observers.

## Risks and Edge Cases

If the buffer is empty on `close`, no EOF chunk is sent; completion is the final signal. `write` catches exceptions and calls `onError` but does not rethrow. The chunk `readOffset` is based on bytes emitted so far and should remain monotonic.

## Test Signals

Tests should cover single-byte and array writes, offset/length validation, chunk boundaries, offsets and lengths across multiple flushes, close completion, empty close behavior, observer error on write exception, and total byte logging.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMGrpcOutputStream.java -->
