# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/TestReclaimableFilter.java

## Purpose
`TestReclaimableFilter` validates the base `ReclaimableFilter` snapshot-chain initialization, bucket/volume validation, locking behavior, active-object-store behavior, and failure handling for inactive or unflushed snapshots.

## Important APIs, Types, and Functions
- An anonymous `ReclaimableFilter<Boolean>` implementation extracts volume and bucket from a slash-separated key and treats `null` or `true` values as reclaimable.
- `testSnapshotInitAndLocking` asserts the filter return value, previous snapshot info list, previous `OmSnapshot` handles, and recorded lock IDs.
- Parameter providers generate combinations of previous snapshot count, actual chain length, and current index.
- `SnapshotUtils` static methods are stubbed by the base class and adjusted in dynamic snapshot-addition tests.

## Control Flow
The main parameterized test applies the filter to valid volume/bucket entries and asserts previous snapshot window initialization. Invalid volume and invalid bucket cases represent active object store mode and expect reclaimability to default true when the object cannot be resolved. Bucket/volume mismatch cases throw when a current snapshot is bound but the key belongs to another bucket. Snapshot-addition tests simulate new latest snapshots during `isReclaimable`. Inactive and unflushed snapshot tests modify specific chain entries and assert failures only when the problematic snapshot falls inside the consulted previous-window range.

## State and Persistence Behavior
State is mostly in-memory but models persistent snapshot metadata: `SnapshotInfo.SnapshotStatus`, last transaction info, transaction table value, and snapshot chains. Lock state is persisted in `AtomicReference<List<UUID>>` during each application and checked against expected previous-plus-current snapshot IDs.

## Dependencies and Integration Points
The test exercises base filter interactions with `OzoneManager`, `BucketManager`, `SnapshotChainManager`, `OmSnapshotManager`, `SnapshotUtils`, `TransactionInfo`, `IOzoneManagerLock`, and `SnapshotInfo` lifecycle fields.

## Risks and Edge Cases
It covers invalid buckets/volumes, mismatched snapshot scope, dynamic snapshot addition, deleted snapshots, and unflushed snapshots. A risk is reliance on exact exception message text. Another is that the test's synthetic key parser is simpler than production key encodings.

## Test Signals
This is the broadest signal for reclaimable filter correctness: before concrete filters decide on an entry, the base class must load, validate, lock, and release the correct snapshot context.
