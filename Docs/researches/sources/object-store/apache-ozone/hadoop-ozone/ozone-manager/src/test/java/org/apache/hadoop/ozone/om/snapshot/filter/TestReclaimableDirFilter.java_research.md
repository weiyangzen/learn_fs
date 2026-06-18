# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/TestReclaimableDirFilter.java

## Purpose
`TestReclaimableDirFilter` validates whether deleted directory entries can be reclaimed based on their presence and identity in the immediately previous snapshot.

## Important APIs, Types, and Functions
- `ReclaimableDirFilter` is created with one previous snapshot in scope.
- `KeyManager.getPreviousSnapshotOzoneDirInfo(volumeId, bucketInfo, dirInfo)` supplies previous directory metadata.
- `OmKeyInfo` represents the current deleted directory entry, while `OmDirectoryInfo` represents the previous snapshot's directory entry.
- The helper `testReclaimableDirFilter` wires previous snapshot key managers and asserts filter output.

## Control Flow
Each parameterized test varies the number of snapshots and active index. The helper resolves the previous snapshot, mocks its `KeyManager` if present, stubs current directory volume/bucket names, and applies the filter. A directory with the same object ID in the previous snapshot is not reclaimable; absent previous info or a different object ID is reclaimable.

## State and Persistence Behavior
No durable state is written. The relevant state is snapshot chain position and object ID continuity across snapshots. The base fixture also ensures the GC read lock is acquired for consulted snapshots.

## Dependencies and Integration Points
This test integrates with bucket metadata, volume ID lookup, previous snapshot handles from `OmSnapshotManager`, and `KeyManager` previous-snapshot lookup APIs. It exercises filesystem-optimized directory reclamation behavior.

## Risks and Edge Cases
The test covers no-previous-snapshot and object-ID mismatch cases. It does not cover failures from `getPreviousSnapshotOzoneDirInfo`, malformed directory names, or multiple previous snapshots because directory reclamation only needs one prior state here.

## Test Signals
The test is a focused signal that directory reclamation depends on identity continuity, not merely name presence.
