# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/BlocksEndPoint.java

## Purpose
`BlocksEndPoint` exposes block deletion backlog information grouped by container lifecycle state.

## Important APIs, Types, And Functions
The resource is `@Path("/blocks")`, JSON-producing, and `@AdminOnly`. The main API is `GET /deletePending` through `getBlocksPendingDeletion(limit, prevKey)`. It uses `ContainerBlocksInfoWrapper` and SCM `DELETED_BLOCKS` table entries.

## Control Flow
The endpoint rejects negative limit or previous transaction ID with `406`. It iterates the SCM deleted-blocks table, optionally seeks to `prevKey` and skips it, converts each `DeletedBlocksTransaction` into wrapper metadata, looks up the container state from `ReconContainerManager`, groups by state, and stops when the current state's list reaches the limit.

## State And Persistence
It reads persistent SCM RocksDB state through `DBStore` and the in-memory/container-manager view of container state. It does not mutate data.

## Dependencies And Integration Points
It depends on `ReconStorageContainerManagerFacade`, `ReconContainerManager`, SCMDB `DELETED_BLOCKS`, container IDs, and JAX-RS exceptions.

## Risks
The limit is applied to the size of the currently appended state list, not total records, so responses can exceed the limit across multiple states. Container lookup failures turn into 500. Invalid seek keys can return empty results.

## Test Signals
Tests should cover negative inputs, prevKey seeking/skipping, state grouping, per-state limit behavior, missing container errors, and empty deleted-block tables.
