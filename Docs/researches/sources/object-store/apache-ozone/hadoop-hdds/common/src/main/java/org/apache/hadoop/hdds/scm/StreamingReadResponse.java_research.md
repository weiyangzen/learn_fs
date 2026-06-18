# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/StreamingReadResponse.java

## Purpose
Holds the datanode and gRPC request observer for a streaming read connection and gives it a compact diagnostic name.

## Important APIs, Types, And Functions
Constructor accepts `DatanodeDetails` and `ClientCallStreamObserver<ContainerCommandRequestProto>`. Getters expose both. `toString()` returns a name derived from the datanode UUID suffix.

## Control Flow
Streaming read setup creates this value and passes it to a `StreamingReaderSpi`; callers use the observer to send read requests over the established stream.

## State And Persistence
The object is immutable and transient. It represents an active client-side gRPC stream and does not persist data.

## Dependencies And Integration Points
Depends on datanode details, datanode container protobufs, and Ratis-shaded gRPC. Integrated by `XceiverClientSpi` streaming read hooks.

## Risks And Test Signals
`toString()` assumes the UUID string contains `-`; normal UUIDs do, but tests should cover name generation and observer wiring for stream setup/teardown.
