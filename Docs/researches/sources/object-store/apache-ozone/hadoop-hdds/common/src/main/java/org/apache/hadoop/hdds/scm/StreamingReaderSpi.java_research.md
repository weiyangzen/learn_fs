# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/StreamingReaderSpi.java

## Purpose
SPI for streaming read response consumers. It extends gRPC `StreamObserver` for container command responses and adds a hook to receive the `StreamingReadResponse` request-side handle.

## Important APIs, Types, And Functions
The interface inherits `onNext`, `onError`, and `onCompleted` for `ContainerCommandResponseProto`, and declares `setStreamingReadResponse(StreamingReadResponse)`.

## Control Flow
An `XceiverClientSpi` implementation initializes streaming read, obtains a request observer, wraps it in `StreamingReadResponse`, and injects it into the reader before response callbacks arrive.

## State And Persistence
The interface stores no state. Implementations typically maintain transient stream state and buffers.

## Dependencies And Integration Points
Depends on Ratis-shaded gRPC and datanode container protobufs. Integrated by container client streaming reads.

## Risks And Test Signals
Ordering of `setStreamingReadResponse` versus `onNext` matters for implementations. Tests should cover unsupported clients, setup ordering, response callback handling, and stream completion/error paths.
