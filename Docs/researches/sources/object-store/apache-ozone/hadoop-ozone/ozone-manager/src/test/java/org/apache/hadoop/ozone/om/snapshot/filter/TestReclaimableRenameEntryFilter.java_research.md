# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/TestReclaimableRenameEntryFilter.java

## Purpose
`TestReclaimableRenameEntryFilter` validates reclaimability of rename-table entries by checking whether their target key or directory still exists in the previous snapshot.

## Important APIs, Types, and Functions
- `ReclaimableRenameEntryFilter` is initialized with one previous snapshot.
- Rename table values are strings that point to prior key/directory entries.
- `OMMetadataManager.splitRenameKey` parses the rename key into volume/bucket/object components.
- Previous snapshot `OMMetadataManager.getKeyTable(bucketLayout)` and `getDirectoryTable` are mocked to simulate object-store and filesystem-optimized layouts.

## Control Flow
The helper resolves the previous snapshot, wires its metadata manager to mocked key and directory tables, configures the current key manager metadata manager to split the rename key, and applies the filter. For object-store buckets, presence in the previous key table makes the entry non-reclaimable except at index zero. For FSO buckets, absence from both key and directory tables makes it reclaimable; presence in either file or directory table makes it non-reclaimable when a previous snapshot exists.

## State and Persistence Behavior
State is represented by mocked table contents. `getMockedTable` returns table values from maps; `getFailingMockedTable` protects layout-specific paths by throwing if an irrelevant table is queried. No persistent state changes occur.

## Dependencies and Integration Points
The test integrates bucket layout selection, rename-key parsing, previous snapshot metadata tables, and base reclaimable snapshot chain locking. It covers both `BucketLayout.OBJECT_STORE` and `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

## Risks and Edge Cases
The tests cover file versus directory entries and ensure non-FSO logic does not query directory tables. Risks not covered include malformed rename keys, RocksDB iterator behavior, and exceptions from relevant tables beyond the deliberate failing-table guard.

## Test Signals
This is a targeted signal that rename entries are only safe to reclaim after the object they point to is absent from the relevant previous-snapshot table.
