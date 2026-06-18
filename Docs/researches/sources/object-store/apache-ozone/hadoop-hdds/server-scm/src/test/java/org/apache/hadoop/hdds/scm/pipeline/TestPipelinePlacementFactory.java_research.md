# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelinePlacementFactory.java

Purpose: verifies `PipelinePlacementPolicyFactory` and placement behavior selected by default and rack-scatter policy configuration.

Important APIs and types: uses `PipelinePlacementPolicyFactory`, `PipelinePlacementPolicy`, `SCMContainerPlacementRackScatter`, `PlacementPolicy`, `NetworkTopologyImpl`, `NodeSchemaManager`, `MockNodeManager`, `PipelineStateManagerImpl`, `DatanodeInfo`, and storage/meta-storage reports.

Control flow: setup initializes configuration. `setupRacks` creates rack-aware datanodes, inserts them into a three-level topology, builds `DatanodeInfo` with enough storage and metadata space, spies node manager lookups, and creates a pipeline state manager. Tests check default factory class, configured rack-scatter class, default placement pattern across racks, rack-scatter all-racks behavior, anchor change when the first rack lacks a second node, used-node-aware placement, and combined used/excluded-node placement.

State and persistence behavior: topology and node-manager state are in-memory. Pipeline state manager is RocksDB-backed but these tests mainly need it as policy context, not for persisted pipeline mutations. Datanode storage reports establish space eligibility.

Dependencies and integration points: covers policy factory configuration key `OZONE_SCM_PIPELINE_PLACEMENT_IMPL_KEY`, rack schema initialization, ratis free-space minimum, SCM DB definitions, HA transaction buffer, and node-manager topology.

Risks and edge cases: `setupRacks` accumulates datanodes and `dnInfos` fields across calls within a test instance; JUnit creates fresh instances by default, but changing lifecycle would matter. The rack-scatter test passes `excludedNodes` twice in one call, likely intentionally using an empty list for both used/excluded but easy to misread. Assertions assume deterministic selection order enough to reason about positions.

Test signals: validates policy selection by config and important rack-aware placement rules involving anchors, used nodes, excluded nodes, and rack scatter.
