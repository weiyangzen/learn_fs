# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocolPB/ScmBlockLocationProtocolClientSideTranslatorPB.java

## Purpose
This class is the protobuf client-side implementation of `ScmBlockLocationProtocol`. It converts Java block-location API calls into wrapped `SCMBlockLocationRequest` protobuf messages, sends them through a retry/failover proxy, converts protobuf responses back to domain objects, and normalizes SCM error statuses into `SCMException`.

## Important APIs, Types, And Functions
The constructor accepts `SCMBlockLocationFailoverProxyProvider` and `OzoneConfiguration`, builds a Hadoop `RetryProxy`, and computes `ratisByteLimit` as 90% of the SCM HA Raft appender queue byte limit. `allocateBlock()`, `deleteKeyBlocks()`, `getScmInfo()`, `addSCM()`, `sortDatanodes()`, and `getNetworkTopology()` implement the protocol. Helper methods include `createSCMBlockRequest()`, `submitRequest()`, `handleError()`, `submitDeleteKeyBlocks()`, and recursive `setParent()`.

## Control Flow
Every RPC creates a wrapper with command type, current client version, and trace ID. Allocation validates positive size, encodes Ratis/standalone/EC replication fields, submits `AllocateScmBlock`, and maps returned block IDs and pipelines. Block deletion batches `KeyBlocks` so each submit stays under the computed byte budget. Topology retrieval reconstructs an `InnerNodeImpl` tree and then restores parent links recursively.

## State, Persistence, And Dependencies
State is limited to the RPC proxy, failover provider, and byte limit. It persists nothing. Dependencies include protobuf classes, replication config subclasses, tracing utilities, Hadoop `RetryProxy`, SCM failover provider, `Pipeline`, `AllocatedBlock`, and topology node classes.

## Integration Points
OM and other clients use this translator behind the Java block protocol. It relies on `ScmBlockLocationProtocolPB` for the wire service and `SCMBlockLocationFailoverProxyProvider` for HA behavior.

## Risks
Unsupported replication types throw before RPC. Delete batching depends on serialized protobuf sizes and leaves room for headers by using a fixed 0.9 factor. `handleError()` maps enum ordinals directly to `SCMException.ResultCodes`, so enum ordering compatibility matters. `setParent()` assumes tree nodes are mutable and represented by `InnerNodeImpl`.

## Test Signals
Tests should cover request fields for Ratis, standalone, and EC allocation; delete batching around the byte threshold; non-OK status mapping; trace ID propagation; topology parent restoration; close behavior; and failover retry integration.
