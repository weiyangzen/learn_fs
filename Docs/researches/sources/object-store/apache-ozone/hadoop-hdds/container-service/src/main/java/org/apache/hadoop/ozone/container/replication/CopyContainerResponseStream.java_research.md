# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/CopyContainerResponseStream.java

Purpose: adapts an `OutputStream` write path to gRPC `CopyContainerResponseProto` messages for pull-replication downloads.

Important APIs and functions: the constructor passes the gRPC `CallStreamObserver`, container ID, and buffer size to `GrpcOutputStream`. `sendPart` builds a response containing container ID, data bytes, EOF flag, current read offset from `getWrittenBytes()`, and chunk length, then calls `onNext`.

Control flow and state: buffering, ready/backpressure waiting, byte counting, and final `onCompleted` are inherited from `GrpcOutputStream`. The offset is computed before the inherited byte counter is incremented, so it represents the starting offset of the message.

Dependencies and integration: created by `GrpcReplicationService.download`; its output is consumed by `GrpcReplicationClient.StreamDownloader`.

Risks and test signals: offset/length correctness and EOF semantics must match the downloader's expectations. Tests should cover multi-chunk streams, exact-buffer-size boundaries, final partial chunk, backpressure delay, and remote cancellation/error propagation.
