# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconStorageContainerSyncHelper.java

## Purpose
Focused mock-based unit tests for `ReconStorageContainerSyncHelper`. It verifies metrics, missing-container add behavior, pagination batching, skip behavior for existing containers, and benign handling of empty SCM lists.

## Important APIs, types, and functions
- Instantiates `ReconStorageContainerSyncHelper` with mocked `StorageContainerServiceProvider` and `ReconContainerManager`.
- Uses `ReconScmContainerSyncMetrics`, `getContainerCount`, `getContainerStateCount`, `getListOfContainerIDs`, `getExistContainerWithPipelinesInBatch`, `addNewContainer`, `updateContainerState`, and `getContainer`.
- Configures `OZONE_RECON_SCM_CONTAINER_ID_BATCH_SIZE` for pagination.

## Control flow
Setup creates metrics and a helper with default config; teardown unregisters metrics. One test feeds SCM and Recon counts for all tracked states and verifies drift and duration metrics. Missing-container tests stub CLOSED ID pages and batch SCM fetches, then verify only absent containers are added, including multi-page behavior with batch fetch for only missing IDs. Existing-container and zero-count tests verify no add/update/fetch occurs. Empty-list handling verifies an SCM count/list race returns true without mutations.

## State and persistence behavior
All state is mocked except metrics. The helper's observable effects are calls to the mocked container manager and metrics updates. No RocksDB persistence is exercised here; that is covered by the integration suite.

## Dependencies and integration points
This file isolates SCM RPC pagination, Recon container manager mutation calls, and sync metrics. It complements `TestReconSCMContainerSyncIntegration` by pinning call-level behavior.

## Risks and edge cases
SCM count/list operations are not atomic, so empty pages must not always be treated as fatal. Batch fetch should include only missing IDs to avoid unnecessary RPC and duplicate additions. Metrics must record drift before sync mutations.

## Test signals
Signals are metric drift values/durations, boolean sync results, exact `addNewContainer` calls, no update/add calls in skip paths, no batch fetch for existing containers, and expected paginated `getListOfContainerIDs` invocations.
