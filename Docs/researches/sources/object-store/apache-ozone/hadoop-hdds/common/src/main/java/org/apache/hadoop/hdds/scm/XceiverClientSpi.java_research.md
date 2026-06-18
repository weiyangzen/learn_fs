# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientSpi.java

## Purpose
Abstract base for storage container protocol clients. It manages cache reference counting/eviction and defines synchronous, asynchronous, streaming, commit-watch, and all-node command APIs for concrete clients.

## Important APIs, Types, And Functions
Key methods include `connect`, `close`, `getPipeline`, `sendCommand`, `sendCommandAsync`, `getPipelineType`, `watchForCommit`, `getReplicatedMinCommitIndex`, and `sendCommandOnAllNodes`. Nested `Validator` validates request/response pairs. Package-private `incrementReference`, `decrementReference`, and `setEvicted` drive lifecycle cleanup.

## Control Flow
Managers increment references when lending clients and decrement on release. If a client has been evicted and refcount reaches zero, `cleanup()` calls `close()`. Synchronous `sendCommand` waits for `sendCommandAsync`, re-interrupts on `InterruptedException`, wraps execution errors with debug-formatted request context, and optionally runs validators.

## State And Persistence
The class holds transient `AtomicInteger referenceCount` and eviction flag. It does not persist data; concrete clients communicate with datanodes and Ratis.

## Dependencies And Integration Points
Depends on `HddsUtils`, container protobufs, `BlockID`, `Pipeline`, datanode details, and Ratis checked consumers. Integrated by `XceiverClientManager`, block I/O, replication, and container operations.

## Risks And Test Signals
`isEvicted` is not volatile, so lifecycle access relies on manager discipline. Default streaming methods throw unsupported exceptions. Tests should cover refcount/eviction close timing, interrupt handling, validator failures, all-node fanout, and commit-watch behavior in concrete clients.
