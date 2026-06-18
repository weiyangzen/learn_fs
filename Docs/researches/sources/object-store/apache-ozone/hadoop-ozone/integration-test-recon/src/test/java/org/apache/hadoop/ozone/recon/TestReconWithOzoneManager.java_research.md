# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconWithOzoneManager.java

## Purpose

This integration test validates Recon synchronization from a non-HA Ozone Manager. It checks full snapshot sync, delta update sync, restart behavior, task-status REST reporting, sequence-number lag metrics, and fallback to full snapshot when Recon's local OM snapshot sequence number is ahead of active OM.

## Important APIs, types, and functions

The class uses `MiniOzoneCluster`, `ReconService`, `OzoneManagerServiceProviderImpl`, `OzoneManagerSyncMetrics`, `OMMetadataManager`, `RDBStore`, task names `OmSnapshotRequest` and `OmDeltaRequest`, Apache `CloseableHttpClient`, and OM metadata types `OmKeyInfo`, `OmKeyLocationInfo`, and `OmKeyLocationInfoGroup`. Test methods are `testOmDBSyncing()` and `testOmDBSyncWithSeqNumberMismatch()`. Helpers include `makeHttpCall()`, `getReconTaskAttributeFromJson()`, `addKeys()`, `writeDataToOm()`, and block-location builders.

## Control flow, state, and persistence

Setup configures Recon OM delta update limit, starts a one-datanode mini cluster with Recon, exits SCM safe mode, and creates an HTTP client for `/api/v1/task/status`. Tests write synthetic key metadata directly into OM's key table, call `syncDataFromOM()`, read OM and Recon RocksDB sequence numbers, and parse task-status JSON for last updated sequence number and timestamp. The mismatch test mutates Recon's OM snapshot DB directly to increment its sequence number beyond OM, then verifies the failed delta update path logs the expected DBUpdates failure and normalizes by full snapshot.

## Dependencies and integration points

The tests integrate OM RocksDB sequence numbers, Recon snapshot and delta sync tasks, metrics lag accounting, task-status REST JSON, and Recon restart. Direct metadata table writes avoid client-level volume/bucket creation but depend on OM key-table semantics and synthetic block locations.

## Risks and test signals

Direct RocksDB table mutation is efficient but bypasses higher-level invariants. The HTTP timeout configuration appears to map variables inconsistently by name, though the test only needs a functioning client. Positive signals are OM and Recon sequence numbers matching, zero sequence-number lag, delta task status advancing after new keys and restart, logs containing the expected failed-update messages for the mismatch, and later logs showing successful DB update.
