# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconSCMContainerSyncIntegration.java

## Purpose
Large integration-style suite for `ReconStorageContainerSyncHelper` using a real `ReconContainerManager` and mocked SCM RPC provider. It validates all four container synchronization passes and large-scale end-to-end state correction without a live cluster.

## Important APIs, types, and functions
- Exercises `syncWithSCMContainerInfo`, `getContainerCount`, `getListOfContainerIDs`, `getExistContainerWithPipelinesInBatch`, `getListOfContainerInfos`, and real `ReconContainerManager` state APIs.
- Uses lifecycle states OPEN, CLOSING, CLOSED, QUASI_CLOSED, DELETING, and DELETED plus lifecycle events `FINALIZE` and `DELETE`.
- Configures `OZONE_RECON_SCM_CONTAINER_ID_BATCH_SIZE` and `OZONE_RECON_SCM_DELETED_CONTAINER_CHECK_BATCH_SIZE`.
- Uses `ReconScmContainerSyncMetrics` and helper methods `seedRecon`, `seedReconAsClosing`, `containerCwp`, `containerInfo`, and `idRange`.

## Control flow
The class groups scenarios by sync pass. Pass 1 adds missing CLOSED containers and corrects OPEN, CLOSING, and QUASI_CLOSED to CLOSED, including multi-page and mixed existing/missing pages. Pass 2 adds missing OPEN containers only, avoids downgrading already-advanced containers, tolerates null pipelines, and verifies cursor behavior across repeated syncs. Pass 3 adds QUASI_CLOSED containers, handles null pipelines, skips existing/closed containers, and advances OPEN/CLOSING to QUASI_CLOSED. Pass 4 scans SCM's DELETED list, retires CLOSED/QUASI_CLOSED/DELETING/OPEN containers to DELETED, adds missing DELETED containers via info lookup, and respects deleted-list batch size. Large-scale tests run 100,000-container corrections, retirements, a mixed 100,000-container scenario, idempotent reruns, and exhaustive transition groups.

## State and persistence behavior
Recon state is real RocksDB-backed container manager state from the base fixture. SCM state is represented through mocked count/list/batch RPCs. Sync mutates container records by adding absent containers, applying lifecycle events to stale containers, and retiring containers present in SCM's deleted list. Null pipelines are intentionally accepted for non-live or cleaned-up SCM cases.

## Dependencies and integration points
The suite tests the integration of SCM service-provider pagination, Recon container lifecycle state machine, container DB persistence, sync metrics, and batch-size configuration. It also validates behavior expected by `ReconStorageContainerManagerFacade.triggerSCMContainerSync`.

## Risks and edge cases
Risks include off-by-one pagination cursors, non-atomic SCM count/list races, silent skipping when SCM returns null pipelines, accidental downgrades from CLOSED to OPEN/QUASI_CLOSED, partial sync reporting, and large-batch performance. The `@Timeout(120)` signal means several tests are intentionally heavy.

## Test signals
Signals are final container counts by state, exact lifecycle states for specific IDs, successful sync return values, partial/error-tolerant return behavior, Mockito call counts for pagination and info lookup, idempotent second sync counts, and 100,000-container state distributions.
