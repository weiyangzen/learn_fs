# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/BlockManagerImpl.java

## Purpose
`BlockManagerImpl` implements block metadata operations for key-value containers: put/commit, closed-container put, finalize, get, list, existence, committed length, and DB cache shutdown.

## Important APIs, Types, And Functions
Important methods are `putBlock`, `putBlockForClosedContainer`, `persistPutBlock`, `finalizeBlock`, `getBlock`, `getCommittedBlockLength`, read-buffer configuration getters, `listBlock`, `blockExists`, and `shutdown`. Helpers include `mergeLastChunkForBlockFinalization`, `getBlockByID`, and `isPartialChunkList`.

## Control Flow
`persistPutBlock` opens DB, ignores stale nonzero BCSIDs as replay, determines whether block count should increment using pending-put cache and DB lookups, gates incremental chunk lists on upgrade finalization, writes block data and BCSID/bytes/block-count metadata in one batch, updates in-memory BCSID/statistics, and manages pending put-block cache. Closed-container puts use similar batching with optional BCSID overwrite for reconciliation. Finalize writes a finalized-block table entry and merges incremental last-chunk metadata.

## State And Persistence
It persists block data, BCSID, bytes used, block count, and finalized-block local IDs in RocksDB. It updates in-memory `KeyValueContainerData` statistics and `KeyValueContainer` pending put-block state. Deletion is unsupported because block deletion is handled by `BlockDeletingService`.

## Dependencies And Integration Points
Dependencies include `BlockUtils`, `KeyValueContainer`, `KeyValueContainerData`, `DatanodeStore` batch/table APIs, `VersionedDatanodeFeatures`, `HDDSLayoutFeature.HBASE_SUPPORT`, and read-buffer config keys. It is called by `KeyValueHandler`, chunk read offset logic, and reconciliation.

## Risks And Test Signals
Risks include BCSID idempotency mistakes, block-count overcounting, batch atomicity, upgrade-gate regressions, finalize merge semantics, and cache cleanup after failures. Tests should cover stale/increasing BCSIDs, new/existing blocks, incremental chunk-list puts, end-of-block cache removal, closed-container puts with partial repair, finalized-block persistence, list ranges, and unsupported delete.
