# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockXceiverClientFactory.java

## Purpose
`MockXceiverClientFactory` provides datanode xceiver clients backed by per-datanode `MockDatanodeStorage` instances. It replaces SCM/datanode networking in client unit tests.

## Important APIs, Types, And Functions
`acquireClient(Pipeline)` and `acquireClient(Pipeline, boolean topologyAware)` return `MockXceiverClientSpi` objects using storage for the first node or closest node. `acquireClientForReadData` uses the pipeline first node. `setFailedStorages` and `mockStorageFailure` queue or apply injected `IOException`s to selected datanodes. `getStorages` exposes the storage map for assertions.

## Control Flow
When a client is acquired, the factory creates or reuses storage for the target datanode. It then scans pending failure reasons and applies any failures whose datanode storage now exists. Failure injection can be requested before storage materialization; pending datanode sets are kept until applied.

## State And Persistence Behavior
The factory stores a concurrent map of datanode details to mock storage and a concurrent map of pending exception reasons to datanode sets. Close and release methods are no-ops. Persistence is in-memory only.

## Dependencies And Integration Points
It implements `XceiverClientFactory`, returns `MockXceiverClientSpi`, and integrates with `RpcClient` through test overrides. EC tests rely on `getStorages` for validating data/parity layout and on failure injection for retry behavior.

## Risks And Edge Cases
Exception objects are used as map keys for pending failures, so equality is by object identity unless an exception overrides it. Release/invalidation behavior is not modeled. Topology-aware acquisition is reduced to closest-node selection. Pending failure application iterates concurrent sets and removes items while iterating, which is supported by concurrent key sets but still test-model-specific.

## Test Signals
`TestOzoneECClient` validates failure injection, exclude-list behavior, retry allocation, and storage counts. `TestOzoneClient` and checksum tests use it for basic key IO and checksum block fetches.
