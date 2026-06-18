# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/recon/TestReconWithOzoneManagerHA.java

## Purpose

This integration test validates Recon behavior with an HA Ozone Manager cluster. It verifies that Recon downloads OM snapshots from the current leader and that container-to-key metadata indexing works after syncing HA OM data.

## Important APIs, types, and functions

The class uses `MiniOzoneHAClusterImpl`, `ReconService`, `OzoneClientFactory.getRpcClient()`, `ObjectStore`, `OzoneManagerServiceProviderImpl`, `ReconTaskControllerImpl`, `ReconContainerMetadataManagerImpl`, `TestReconOmMetaManagerUtils`, `OZONE_DB_CHECKPOINT_HTTP_ENDPOINT`, and OM lookup types `OmKeyArgs` and `OmKeyLocationInfo`. The main test is `testReconGetsSnapshotFromLeader()`, with helper `getContainerIdForKey()`.

## Control flow, state, and persistence

Setup enables RocksDB sync-to-disk, builds a three-OM/one-datanode HA mini cluster, starts Recon as an added service, creates a test volume, and creates an OBJECT_STORE bucket because Recon's container ID to key mapping does not yet support FSO buckets. The test waits for leader election, constructs the expected leader checkpoint URL, compares it with `getOzoneManagerSnapshotUrl()`, writes a RATIS ONE key, calls `syncDataFromOM()`, waits for Recon event-buffer completion, waits until the expected container has at least one key in Recon's container metadata manager, and finally verifies the stored key prefix.

## Dependencies and integration points

The test integrates OM HA leader discovery, HTTP checkpoint URL construction, Recon OM sync, asynchronous Recon task processing, and Recon's container-key table. It deliberately reads the key from the current OM leader to find the authoritative block/container ID.

## Risks and test signals

Leader readiness is asynchronous, so a long wait guards election. The test only covers OBJECT_STORE bucket layout due to a known FSO limitation. Positive signals are an expected snapshot URL pointing to the leader's HTTP server, successful sync after key creation, event-buffer drain, container-key count convergence, and a key prefix of `/testrecon/testrecon/ratis` in Recon metadata.
