# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMBlockProtocolServer.java

## Purpose
`TestSCMBlockProtocolServer` verifies block-protocol datanode sorting relative to a client and allocation-time ordering of pipeline nodes. It focuses on network topology awareness for both datanode clients and edge/non-datanode clients.

## Important APIs, Types, and Functions
- `SCMBlockProtocolServer.sortDatanodes` and `allocateBlock` are under test.
- `ScmBlockLocationProtocolServerSideTranslatorPB.sortDatanodes` tests the protobuf service path.
- Inner `BlockManagerStub.allocateBlock` creates random open Ratis/THREE pipelines for allocation tests.
- Helpers `getNetworkNames`, `nodeAddress`, and `assertRackOrder` encapsulate topology assertions.

## Control Flow
Setup creates an SCM with static rack mapping for ten datanodes and two edge nodes, starts SCM, exits safe mode, registers datanodes, and captures the block protocol server and translator. Sorting tests call the server for each datanode client and each edge node. Additional test cases cover illegal client addresses, unknown requested nodes, and all-unknown requested nodes. Allocation test requests multiple blocks with a client machine and asserts any client-local datanode appears first and same-rack nodes are ordered before other-rack nodes.

## State and Persistence Behavior
SCM is a real test instance with temp metadata, but the block manager is a stub. Node registration populates SCM node manager topology state. Allocated blocks are generated on demand and not persisted by the stub.

## Dependencies and Integration Points
The test integrates SCM startup, static network topology mapping, node manager registration, block protocol server, protobuf translator, and block manager allocation. It uses `ClientVersion.CURRENT_VERSION` for the translator call.

## Risks and Edge Cases
Covered edge cases include client specified by IP/hostname setting, non-datanode clients that still have topology mapping, illegal client identifiers, unknown node network names mixed with known ones, and all unknown nodes returning an empty response. Allocation ordering is checked without assuming every pipeline contains the client datanode.

## Test Signals
The rack-order assertions protect locality behavior: client node first when present, same-rack nodes before cross-rack nodes, and unknown nodes filtered from service responses.
