# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconStorageContainerManagerFacade.java

## Purpose
Tests `ReconStorageContainerManagerFacade` snapshot DB replacement and container sync metric/status handling. It verifies SCM DB snapshots are opened from Recon's canonical path and that manual container sync reports success/failure duration consistently.

## Important APIs, types, and functions
- Uses `ReconTestInjector` to build a real Recon facade with Recon SQL DB, OM metadata manager, container DB, and mocked service providers.
- Exercises `updateReconSCMDBWithNewSnapshot`, `getScmDBStore`, and `triggerSCMContainerSync`.
- Uses `DBCheckpoint`, `DBStoreBuilder`, `ReconSCMDBDefinition.RECON_SCM_DB_NAME`, `ReconScmContainerSyncMetrics`, and reflection to replace/read private `containerSyncHelper` and `containerSyncMetrics`.

## Control flow
The snapshot test creates a temporary SCM checkpoint DB under a non-canonical snapshot name, mocks `getSCMDBSnapshot`, calls `updateReconSCMDBWithNewSnapshot`, and checks the facade opened the DB at the canonical `recon-scm.db` path, moved data there, and removed the original checkpoint directory. Three sync tests replace the internal helper with a mock returning true, false, or throwing; they call `triggerSCMContainerSync` and assert status/duration fields and exception propagation.

## State and persistence behavior
The facade manages a real SCM RocksDB store location. Snapshot import should relocate/open the DB at the canonical Recon SCM DB path rather than leaving Recon pointed at a transient checkpoint directory. Metrics persist only in the registered metrics object and are unregistered after each test.

## Dependencies and integration points
This file integrates dependency injection, Recon OM metadata fixture, storage-container service provider, SCM DB snapshots, and container sync metrics. It is a facade-level guard over lower-level sync helper behavior.

## Risks and edge cases
Private-field reflection makes the tests sensitive to implementation field names. Snapshot path assertions depend on canonical file behavior. Metric unregister cleanup is required to avoid metric registry collisions across tests.

## Test signals
Signals include canonical DB location equality, existence/removal of expected directories, boolean return for sync success/failure, failure status on false or exception, duration updated from sentinel `-1`, and original exception object propagation.
