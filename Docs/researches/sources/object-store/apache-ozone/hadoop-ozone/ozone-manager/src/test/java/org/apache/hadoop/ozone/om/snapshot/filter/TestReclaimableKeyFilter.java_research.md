# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/TestReclaimableKeyFilter.java

## Purpose
`TestReclaimableKeyFilter` validates deleted-key reclamation and exclusive-size accounting across current, previous, and previous-to-previous snapshots.

## Important APIs, Types, and Functions
- `ReclaimableKeyFilter` is initialized with two previous snapshots in scope.
- `KeyManager.getPreviousSnapshotOzoneKeyInfo(volumeId, bucketInfo, keyInfo)` retrieves prior key versions.
- `SnapshotUtils.isBlockLocationInfoSame` is mocked to distinguish same-object/same-block continuity from changed block locations.
- `getExclusiveSizeMap` and `getExclusiveReplicatedSizeMap` expose per-snapshot retained-size accounting.

## Control Flow
The helper resolves two prior snapshots, attaches mock key managers to them, wires previous-key lookups, and applies the filter. A key is not reclaimable when the previous snapshot contains the same object ID and equivalent block locations. It is reclaimable when there is no prior key, a different object ID, or different block IDs. Size-accounting tests apply the filter multiple times while changing previous-to-previous block equivalence to verify when the previous snapshot's exclusive size should accumulate.

## State and Persistence Behavior
The main state under test is the filter's in-memory maps keyed by previous snapshot ID. They accumulate data size and replicated size for keys retained exclusively by a snapshot. Snapshot metadata and previous-key tables are mocked; no durable store is mutated.

## Dependencies and Integration Points
This test integrates with key manager previous-snapshot lookup, bucket info, volume ID mapping, snapshot handles, and `SnapshotUtils` block comparison. It protects the snapshot GC accounting path that reports storage exclusive to snapshots.

## Risks and Edge Cases
Covered risks include reclaiming a key that is still referenced by prior snapshots, failing to reclaim changed object/block versions, and incorrect exclusive-size accounting when the same key exists farther back in the chain. The tests use mocked `OmKeyInfo`; real multipart/block-list complexity is represented only through `isBlockLocationInfoSame`.

## Test Signals
The file provides strong coverage for key identity and retained-byte accounting. It is especially useful for regressions that would over-delete snapshot-protected blocks or undercount exclusive snapshot usage.
