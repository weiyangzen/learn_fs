# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestBlockDeletionService.java

## Purpose
Integration tests for OM-to-SCM block deletion payloads, especially replicated and unreplicated quota fields sent with deleted blocks before and after SCM layout upgrade.

## Important APIs and Types
The class `TestBlockDeletionService` uses `MiniOzoneCluster`, `StorageContainerLocationProtocol`, `SCMPerformanceMetrics`, `BlockManager`, `BlockGroup`, `DeletedBlock`, `QuotaUtil`, `ReplicationConfig` variants (`RatisReplicationConfig`, `StandaloneReplicationConfig`, `ECReplicationConfig`), `InjectedUpgradeFinalizationExecutor`, and Mockito `ArgumentCaptor`. Key tests are `testDeleteKeyQuotaWithUpgrade` and parameterized `testDeleteKeyQuotaWithDifferentReplicationTypes`.

## Control Flow
Setup starts a nine-datanode cluster initialized at the `HBASE_SUPPORT` SCM layout with a custom upgrade finalization executor, creates a volume and bucket, and captures SCM metrics. Each test writes a fixed-size key with a specific replication config, injects a Mockito spy into SCM's private `scmBlockManager` field, deletes the key, captures the eventual `deleteBlocks` call, and verifies quota accounting. The upgrade test then finalizes SCM to `STORAGE_SPACE_DISTRIBUTION` and repeats the deletion checks.

## State and Persistence
Persistent state includes OM key metadata, deleted key entries processed by deletion service, SCM block deletion state, SCM layout version, and metrics counters for successful and failed delete-key blocks. Reflection replaces SCM's in-memory block manager with a spy while preserving the real implementation underneath.

## Dependencies and Integration Points
This couples OM key deletion service, SCM block manager RPC path, replication-specific quota calculation, SCM metrics, SCM upgrade finalization, datanode layout version, and mini-cluster object-store writes.

## Risks and Edge Cases
Reflection against `scmBlockManager` is brittle if SCM internals change. Mockito spy injection persists until overwritten, so test ordering could matter. EC configs with large cell sizes are used against small keys, relying on `QuotaUtil` semantics. The tests wait up to 50 seconds for async deletion service calls.

## Test Signals
Signals include exactly one deleted block per key, `DeletedBlock.getReplicatedSize` matching `QuotaUtil.getReplicatedSize`, unreplicated size equal to key size, successful delete metrics incrementing, failed delete metrics remaining unchanged, and behavior remaining stable across SCM layout finalization.
