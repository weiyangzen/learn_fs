# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/ClusterStateEndpoint.java

## Purpose
`ClusterStateEndpoint` returns a high-level summary of Recon's view of the Ozone cluster: containers, datanodes, pipelines, capacity, volume/bucket/key counts, pending deletion, and service IDs.

## Important APIs, Types, And Functions
The resource is `@Path("/clusterState")`. `getClusterState()` builds `ClusterStateResponse`, `ClusterStorageReport`, and `ContainerStateCounts`. It uses a `MISSING_CONTAINER_COUNT_LIMIT` sentinel of 1001.

## Control Flow
The endpoint reads pipeline count, missing-container records, open/deleted container counts, healthy datanode counts, SCM node aggregate stats, per-datanode filesystem usage, and global stats for OM table counts. It sums legacy keys and FSO files, counts deleted keys and deleted dirs, subtracts deleted containers from total, then returns the response.

## State And Persistence
It reads in-memory SCM manager state, container health SQL records, and global stats values populated from OM metadata tasks. It does not mutate state.

## Dependencies And Integration Points
It integrates `ReconNodeManager`, `ReconPipelineManager`, `ReconContainerManager`, `ContainerHealthSchemaManager`, `ReconGlobalStatsManager`, OM table definitions, and Ozone service ID config keys.

## Risks
Filesystem usage may be incomplete when datanodes have not reported. Missing-container count is capped/sentinel-based. Global stats IO failures set some defaults but may leave other counters at zero. Container total subtracts deleted containers from current manager size, so stale deleted state affects totals.

## Test Signals
Tests should assert healthy node counting, storage report fields, missing sentinel behavior, global stats aggregation, deleted-container subtraction, service ID propagation, and behavior when no datanodes or stats exist.
