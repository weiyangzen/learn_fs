<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ScmBlockLocationTestingClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ScmBlockLocationTestingClient.java

Purpose: Fake `ScmBlockLocationProtocol` for OM tests. It allocates synthetic blocks and simulates delete-block success/failure patterns without a real SCM.

Important APIs/types/functions: Constructor sets cluster ID, SCM ID, and delete failure frequency. `allocateBlock` returns one `AllocatedBlock` with a random datanode, standalone ONE open pipeline, and time-based container/local IDs. `deleteKeyBlocks` processes `DeletedBlock`s into `DeleteBlockGroupResult`s. `processBlock` applies success/all-fail/every-Nth-fail behavior. `getScmInfo`, `getNetworkTopology`, `getNumberOfDeletedBlocks`, `addSCM`, `sortDatanodes`, and `close` complete the protocol.

Control flow: Allocation ignores requested count and returns a singleton block. Delete calls increment a call counter per block, choose success or `unknownFailure`, and increment `numBlocksDeleted` only on success. Blank IDs are replaced with random UUIDs.

State and persistence behavior: No persistence. Maintains counters for current delete call and number of pseudo-deleted blocks.

Dependencies and integration points: Used by `OmTestManagers` and delete/key tests. Integrates HDDS block, pipeline, datanode, topology, and Ozone delete result helper classes.

Risks: `allocateBlock` ignores `num`, requested replication config, owner, excludes, and client machine; it is only valid for tests that need any block. `sortDatanodes` returns null, which can break code paths expecting sorted nodes. Time-based IDs can collide in extremely tight loops. Failure frequency applies per block, not per request group.

Test signals: Tests should assert delete count behavior for frequency 0, 1, and N; allocation shape; SCM info propagation; and that callers do not rely on unsupported methods.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ScmBlockLocationTestingClient.java -->
