## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/SnapshotUtils.java

Purpose: utility holder for common snapshot lookup, activity validation, chain traversal, deleted-table merge, previous-snapshot validation, and key block-location comparison.

Important APIs and types: `getSnapshotInfo` overloads resolve snapshots by volume/bucket/name, table key, or UUID plus `SnapshotChainManager`; `checkSnapshotActive` validates `SNAPSHOT_ACTIVE`; `getNextSnapshot`, `getPreviousSnapshot`, and `getPreviousSnapshotId` navigate path chains; `createMergedRepeatedOmKeyInfoFromDeletedTableEntry` merges snapshot move protobuf key versions into deleted table entries; `getLatestSnapshotInfo` and `getLatestPathSnapshotId` query chain tails; `validatePreviousSnapshotId` enforces expected chain predecessor; `isBlockLocationInfoSame` compares key block lists, with an hsync object-ID shortcut.

Control flow: lookup functions read OM metadata tables and translate null/missing entries to `OMException(FILE_NOT_FOUND)`. Chain functions tolerate `NoSuchElementException` from in-memory chain lag after purge. Deleted-table merge converts protobuf key infos, reads any existing `RepeatedOmKeyInfo`, and appends only if the new list is not already the latest suffix. Block comparison handles nulls, hsync keys, version group counts, latest version locations, and per-block identity.

State and persistence: the class does not own state. It reads snapshot metadata, deleted table entries, and chain manager indexes; the deleted-table merge returns a value to be persisted by the caller.

Dependencies and integration: used broadly by diff generation, reclaim filters, defrag, purge, and request validation paths. It depends on `OzoneManager`, `OMMetadataManager`, `SnapshotChainManager`, OM protobufs, and `OmKeyInfo` location models.

Risks and edge cases: `dropColumnFamilyHandle` converts RocksDB failures into runtime exceptions. Chain helpers return null at chain ends, but some callers must handle null snapshot infos carefully. `createMergedRepeatedOmKeyInfoFromDeletedTableEntry` relies on list equality and suffix ordering to avoid duplicate replay additions. Hsync block comparison treats same object ID as same key even when block locations differ, which is intentional but should remain isolated to hsync semantics.

Test signals: cover missing snapshot table entries, inactive snapshots, chain races around purged snapshots, previous-id validation for AOS/null snapshot cases, idempotent deleted-table merge on replay, hsync versus non-hsync block comparison, and null/latest-location handling.
