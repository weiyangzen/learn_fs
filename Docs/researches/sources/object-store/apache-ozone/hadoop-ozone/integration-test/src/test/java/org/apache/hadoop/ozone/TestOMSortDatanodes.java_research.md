# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestOMSortDatanodes.java

## Purpose
`TestOMSortDatanodes` verifies network-topology-aware read ordering as exposed through `KeyManagerImpl.sortDatanodes(List, String)`. It builds a miniature SCM/OM manager stack with registered datanodes distributed across two racks and validates that datanodes are sorted nearest to either a datanode client or an edge client hostname.

## Important APIs, Types, and Functions
- `KeyManagerImpl.sortDatanodes` is the primary API under test.
- `StaticMapping` and `NET_TOPOLOGY_NODE_SWITCH_MAPPING_IMPL_KEY` provide deterministic host/IP-to-rack resolution.
- `OZONE_NETWORK_TOPOLOGY_AWARE_READ_KEY` enables topology-aware read sorting.
- `HddsTestUtils.getScm`, `SCMConfigurator`, `SCMHAManagerStub`, `SCMContext.emptyContext`, `NodeManager.register`, and `OmTestManagers` create the SCM and OM-side dependencies.
- Helpers `assertRackOrder` and `nodeAddress` encode expected ordering and hostname-vs-IP client addressing.

## Control Flow
`setup` creates ten random datanodes, alternates them between `/rack0` and `/rack1`, adds both hostname and IP mappings, and adds two synthetic edge nodes. SCM is started, safe mode is exited, all datanodes are registered with the SCM node manager, and `OmTestManagers` creates an OzoneManager, RPC client, and key manager. `sortDatanodesRelativeToDatanode` iterates every registered datanode and expects the source datanode to be first, followed by all same-rack nodes before other-rack nodes. `sortDatanodesRelativeToNonDatanode` uses the edge hostnames and checks same-rack-first ordering. `testSortDatanodes` covers valid datanode client address and invalid client strings, asserting the method remains total and returns the full node list.

## State and Persistence Behavior
The test registers datanodes into SCM's in-memory node manager and uses static topology mappings from configuration. It does not persist OM keys or blocks. Cleanup closes the Ozone client, stops and joins SCM, and stops OM.

## Dependencies and Integration Points
This is an integration point between Hadoop network topology mapping, SCM node registration, OM key-management read sorting, and Ozone client manager setup. It also checks that `DatanodeDetails` network levels are set to `ROOT_LEVEL + 2`, matching rack-level topology.

## Risks and Edge Cases
The rack-order assertion assumes an even split across exactly two racks and checks the first half versus second half, so changes to distribution or topology depth would require test changes. Invalid clients are tested only for result size, not stable order. Because datanodes are random, uniqueness and mapping correctness depend on generated host/IP values being stable enough for `StaticMapping`.

## Test Signals
The most important signal is that source-local reads rank the source datanode first, same-rack nodes before remote-rack nodes, and invalid client addresses do not drop datanodes. This protects topology-aware read performance and fallback behavior.
