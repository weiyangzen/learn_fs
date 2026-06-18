<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/NodeEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/NodeEndpoint.java

## Purpose

`NodeEndpoint` serves `/datanodes` APIs for datanode inventory, safe removal from Recon state, and decommission-status reporting.

## Important APIs and Types

`getDatanodes` returns `DatanodesResponse` with `DatanodeMetadata`, storage reports, pipeline metadata, leader counts, and open-container counts. `removeDatanodes` accepts a JSON list of UUIDs and returns grouped removed/failed/not-found results. Decommission APIs return details for all or one decommissioning datanode.

## Control Flow

Inventory loops over `ReconNodeManager.getAllNodes`, builds storage reports from `SCMNodeStat` and filesystem usage, resolves node health, pipelines, pipeline leaders, and container counts. Removal validates non-null/non-empty UUIDs, resolves each node, requires it to be DEAD, checks for open containers and open pipelines, then calls `nodeManager.removeNode`. Decommission reporting queries SCM for `DECOMMISSIONING` nodes, filters by uuid/ip, reads decommission metrics JSON, and includes container lists per datanode.

## State and Persistence

Most APIs are read-only views of Recon's in-memory SCM/node managers and SCM protocol. `removeDatanodes` mutates Recon node manager state and its nodes table in Recon DB through `ReconNodeManager.removeNode`.

## Dependencies and Integration Points

It depends on `ReconNodeManager`, `ReconPipelineManager`, `ReconContainerManager`, `StorageContainerLocationProtocol`, SCM node/container/pipeline types, `DecommissionUtils`, and client versioned SCM calls.

## Risks and Edge Cases

Removal catches all exceptions around the whole loop, so one unexpected error aborts the entire request. Open container/pipeline checks are best-effort and tolerate missing container/pipeline manager entries with warnings. Decommission metrics parsing returns partial maps when SCM metrics are missing. `getStorageReport` calls `nodeManager.getNodeStat(datanode).get()` without a null check.

## Test Signals

Tests should cover inventory with missing pipeline leaders, missing node state, filesystem stats, successful and failed removals, DEAD-only enforcement, open pipeline/container blocks, invalid UUID lists, not-found UUIDs, decommission filtering by uuid/ip, and absent metrics JSON.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/NodeEndpoint.java -->
