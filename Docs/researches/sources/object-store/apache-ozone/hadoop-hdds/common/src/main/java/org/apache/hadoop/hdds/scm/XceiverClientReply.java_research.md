# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientReply.java

## Purpose
Represents the asynchronous result of an Xceiver client command, including the response future, Ratis log index, and datanodes that produced replies or failures.

## Important APIs, Types, And Functions
`getResponse()`/`setResponse()` manage a `CompletableFuture<ContainerCommandResponseProto>`. `getLogIndex()`/`setLogIndex()` track commit/log index. `addDatanode()` records datanodes and `getDatanodes()` returns an unmodifiable view.

## Control Flow
Client implementations create a reply when sending commands asynchronously. Synchronous `XceiverClientSpi.sendCommand` waits on the response future and validators can inspect the resulting response.

## State And Persistence
All state is in-memory and mutable. The datanode list is not synchronized, so it is expected to be populated in a controlled async path.

## Dependencies And Integration Points
Depends on datanode details and container response protobufs. Integrated by Ratis/standalone Xceiver clients and commit-watch logic.

## Risks And Test Signals
Concurrent mutation can race with readers, and `setResponse` can replace futures after construction. Tests should cover async completion, failed futures, datanode reporting, and log index propagation.
