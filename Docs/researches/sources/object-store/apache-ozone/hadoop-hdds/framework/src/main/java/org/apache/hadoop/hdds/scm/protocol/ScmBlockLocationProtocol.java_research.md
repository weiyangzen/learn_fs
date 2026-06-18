# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocol/ScmBlockLocationProtocol.java

## Purpose
`ScmBlockLocationProtocol` is the public Java RPC contract for clients that need SCM block placement, block deletion, SCM identity, HA membership, datanode sorting, and network topology retrieval.

## Important APIs, Types, And Functions
The interface is `Closeable`, Kerberos-protected with the SCM principal, and exposes `versionID = 1L` for Hadoop RPC compatibility. Core methods include `allocateBlock(...)`, `deleteKeyBlocks(...)`, `getScmInfo()`, `addSCM(...)`, `sortDatanodes(...)`, and `getNetworkTopology()`. Deprecated overloads translate proto replication type/factor into `ReplicationConfig`.

## Control Flow
The interface itself has no server-side implementation, but its default methods funnel older allocation signatures into the newer `ReplicationConfig`-based allocation path and optionally pass a client machine for topology sorting.

## State, Persistence, And Dependencies
There is no local state. The API depends on replication configs, SCM metadata, `AllocatedBlock`, `ExcludeList`, Ozone block group deletion result types, datanode details, and topology `InnerNode`.

## Integration Points
`ScmBlockLocationProtocolClientSideTranslatorPB` implements this interface for protobuf RPC. OM and other clients use it to allocate blocks and delete key block groups. The protocol pairs with `ScmBlockLocationProtocolPB` on the wire.

## Risks
Compatibility depends on preserving `versionID` and semantic behavior of deprecated overloads. The allocation API throws both IO and timeout-related failures across implementations, and callers must supply sensible exclude lists and replication configs.

## Test Signals
Contract tests should verify default overload translation, EC/Ratis/standalone allocation semantics through the translator/server pair, delete result mapping, SCM info retrieval, topology tree retrieval, and Kerberos/protocol annotation compatibility.
