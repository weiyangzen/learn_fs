# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/TestBlocksEndPoint.java

## Purpose
This JUnit test validates `BlocksEndPoint.getBlocksPendingDeletion`, which groups pending deleted-block transactions by container state and supports limit and previous-key pagination.

## Important APIs and functions
`initializeInjector` builds a Recon test graph with SQL DB, Recon OM, SCM facade, container DB, `ContainerEndpoint`, and `BlocksEndPoint`, then captures `ReconContainerManager`, `ReconPipelineManager`, and SCM `DBStore`. `setUp` seeds open containers 100-107. The three tests insert `DeletedBlocksTransaction` rows into the SCM `DELETED_BLOCKS` table and call `getBlocksPendingDeletion(limit, prevKey)`. `getTestContainer` creates a `ContainerWithPipeline` for a given ID and state.

## Control flow, state, and persistence
The test writes SCM deleted-block transactions to the RocksDB table and container state to the Recon SCM facade. `testGetBlocksPendingDeletion` verifies one transaction under `"OPEN"`. `testGetBlocksPendingDeletionLimitParam` verifies only the first row is returned when limit is one. `testGetBlocksPendingDeletionPrevKeyParam` verifies seeking past transaction ID 2 returns TX 3 and seeking at/after existing TX IDs can return empty.

## Dependencies and integration points
Dependencies include `ReconTestInjector`, `OMMetadataManagerTestUtils`, SCM DB definitions, container manager/pipeline manager, protobuf `DeletedBlocksTransaction`, and `ContainerBlocksInfoWrapper`. This test connects SCM table data to endpoint DTOs.

## Risks and edge cases
`isSetupDone` avoids rebuilding the injector but `setUp` repeatedly adds the same container IDs, so test isolation depends on container manager behavior. The tests only cover open containers and do not exercise missing container state mapping, multiple states, or invalid parameters.

## Test signals
Good regression coverage for limit and prev-key semantics over SCM deleted-block transactions and DTO field population (`containerID`, local IDs, count, TX ID).
