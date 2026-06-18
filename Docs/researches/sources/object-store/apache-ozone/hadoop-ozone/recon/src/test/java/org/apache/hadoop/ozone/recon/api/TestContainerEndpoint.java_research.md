# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestContainerEndpoint.java

## Purpose
This large integration-style JUnit test validates `ContainerEndpoint` behavior across container-key lookup, container listing, missing/unhealthy containers, replica history, SCM-deleted containers, OM/SCM mismatch insights, OM containers deleted in SCM, duplicate FSO path reconstruction, and quasi-closed container APIs.

## Important APIs and functions
`initializeInjector` wires Recon OM, SQL DB, SCM facade, container DB, `ContainerEndpoint`, and `ContainerHealthSchemaManager`. `setUp` seeds OM key-location data for legacy/default containers and reprocesses OBS and FSO container-key mapper tasks in parallel. `setUpFSOData` and `setUpDuplicateFSOFileKeys` write FSO volume, bucket, directory, and key table entries. `reprocessContainerKeyMapper` runs `ContainerKeyMapperTaskOBS` and `ContainerKeyMapperTaskFSO`. Helper methods create containers, datanodes, unhealthy records, deleted lifecycle transitions, and pipeline-isolated SCM containers.

## Control flow, state, and persistence
The test exercises both RocksDB-backed OM/SCM state and SQL-backed unhealthy-container state. On repeated setup it clears shared container-key maps, resets truncation flags, and reinitializes container metadata from an empty map to reduce leakage. Tests mutate container lifecycle states through SCM events (`FINALIZE`, `CLOSE`, `DELETE`, `CLEANUP`, `QUASI_CLOSE`), write replica history into Recon container manager, and update OM-to-container mappings through reprocess tasks.

## Endpoint coverage
`getKeysForContainer` is tested for total count, limit, prev-key, legacy key versions/block IDs, FSO file-table keys, and duplicate FSO file names under different directories. `getContainers` is tested for limit, previous key, sequential and non-sequential IDs, and invalid parameters. `getMissingContainers`, `getUnhealthyContainers`, filtered unhealthy states, invalid states, and pagination verify counts, replica histories, checksum mismatch, and expected/actual/delta counts. `getReplicaHistoryForContainer` validates latest history de-duplication and descending order. `getSCMDeletedContainers` covers deleted lifecycle rows with limit and prev key. `getContainerMisMatchInsights` covers containers present only in OM, only in SCM, filter direction, pagination, and per-container pipeline-list isolation. `getOmContainersDeletedInSCM` covers deleted-in-SCM discrepancy rows, count/limit/prev behavior. Quasi-closed tests cover empty, basic, with replicas, pagination, count-only limit zero, invalid inputs, and dedicated count behavior.

## Dependencies and integration points
The test integrates nearly every Recon container subsystem: `ReconContainerMetadataManager`, `ReconNamespaceSummaryManager`, `ReconContainerManager`, `ReconPipelineManager`, `ContainerHealthSchemaManager`, `ContainerKeyMapperTaskOBS/FSO`, `NSSummaryTaskWithFSO`, OM metadata helpers, SCM lifecycle state machine, and endpoint DTOs such as `KeysResponse`, `ContainersResponse`, `UnhealthyContainersResponse`, `ContainerDiscrepancyInfo`, and `QuasiClosedContainersResponse`.

## Risks and edge cases
The class is marked `@Flaky("HDDS-14178")`, reflecting real isolation or timing sensitivity. It uses shared state and concurrent mapper reprocessing, so cleanup order is important. FSO tests depend on exact object IDs and path keys. Pagination tests assume sorted container IDs and stable RocksDB iteration. Mismatch tests manipulate mappings directly with batch deletes, which is powerful but can bypass invariants. Duplicate FSO setup intentionally uses repeated object/key values and is sensitive to endpoint path reconstruction logic.

## Test signals
This is the strongest test signal in the subset for container endpoints and related Recon tasks. It covers many production workflows and known regressions: table truncation/shared maps, FSO/OBS mapper interaction, unhealthy state compatibility, checksum mismatch, OM/SCM discrepancy direction, and quasi-closed response contracts.
