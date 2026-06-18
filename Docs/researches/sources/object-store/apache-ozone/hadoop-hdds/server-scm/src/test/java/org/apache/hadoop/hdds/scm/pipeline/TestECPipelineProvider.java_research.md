# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestECPipelineProvider.java

Purpose: verifies EC pipeline creation and read-pipeline construction in `ECPipelineProvider`.

Important APIs and types: uses `ECPipelineProvider`, `PipelineProvider`, `ECReplicationConfig`, `Pipeline`, `PipelineStateManager`, `PlacementPolicy`, `NodeManager`, `ContainerReplica`, and `NodeStatus`.

Control flow: setup mocks placement policy to return the requested number of random datanodes and mocks all node statuses as in-service healthy by default. Creation tests assert EC type, required node count, allocated state, and one-based replica indexes. Read tests build `ContainerReplica` sets and assert read pipelines preserve replica indexes. Additional tests mark some replica nodes dead and expect omission, add duplicate replica indexes on healthy/decommissioning/stale nodes and expect sorted output, and verify excluded/favored lists plus container-size bytes are passed to placement policy.

State and persistence behavior: provider returns pipeline objects but state manager is mocked, so no real persistence occurs. Replica-index state is stored in the pipeline's datanode-to-index map. Read-pipeline node selection is derived from current `NodeManager.getNodeStatus` calls.

Dependencies and integration points: integrates EC replication config, SCM placement policy API, Ozone container size configuration, container replica metadata, and node health/operational status ordering.

Risks and edge cases: mocked placement policy masks real rack and capacity behavior. `HashSet` replica iteration order is not deterministic, but assertions use sets or ordered groups matching comparator categories. Dead-node omission depends on node-manager status lookup for each replica datanode.

Test signals: strong signal for EC required-node sizing, index numbering, read-path filtering/sorting, and propagation of placement constraints.
