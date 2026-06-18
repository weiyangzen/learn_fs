<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/GrpcXceiverService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/GrpcXceiverService.java

## Purpose

`GrpcXceiverService` is the datanode gRPC service implementation for container command RPCs. It wraps `XceiverClientProtocolServiceGrpc`, replaces the streaming `send` request marshaller with a Ratis zero-copy marshaller, and dispatches each client command into `ContainerDispatcher`. The complete 160-line file was read.

## Important APIs, Types, and Functions

The class extends `XceiverClientProtocolServiceGrpc.XceiverClientProtocolServiceImplBase`. Main APIs are `bindServiceWithZeroCopy()`, static `addZeroCopyMethod(...)`, and overridden `send(StreamObserver<ContainerCommandResponseProto>)`. It owns a `ZeroCopyMessageMarshaller<ContainerCommandRequestProto>` and uses `RandomAccessFileChannel` for streaming block reads.

## Control Flow

`bindServiceWithZeroCopy` copies the generated service definition, replaces only the `send` method request marshaller, and leaves other methods unchanged. `send` returns a `StreamObserver` that processes each incoming `ContainerCommandRequestProto`. `ReadChunk` gets a release-supporting `DispatcherContext`; `ReadBlock` is routed to `dispatcher.streamDataReadOnly` with a reusable `RandomAccessFileChannel`; all other commands call `dispatcher.dispatch` and emit one response. Each request is released from the zero-copy marshaller in `finally`, and the dispatcher context release hook is invoked when present.

## State and Persistence Behavior

The service holds dispatcher and marshaller references. Each stream observer owns a closed flag and a block-file channel, closing it on error or completion. Persistence belongs to the dispatcher and lower container handlers, not this service.

## Dependencies and Integration Points

It integrates with generated datanode protobuf gRPC service bindings, Ratis shaded gRPC classes, `ZeroCopyMessageMarshaller`, `ContainerDispatcher`, `DispatcherContext`, and random-access file channels used for read streaming.

## Risks and Edge Cases

`context` is only created for `ReadChunk`, so `ReadBlock` streaming receives null context in this implementation. Any dispatcher exception closes the stream and propagates `onError`. Cancelled gRPC status is intentionally ignored in `onError`; other errors are logged. Missing release calls would leak zero-copy buffers, so the `finally` path is important.

## Test Signals

Tests should cover service definition replacement for `send`, zero-copy release on success and exception, read-block streaming path, normal dispatch path, cancelled error handling, idempotent close on concurrent terminal callbacks, and release-supported `ReadChunk` context behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/GrpcXceiverService.java -->
