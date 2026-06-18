## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneSnapshot.java

### Purpose
`OzoneSnapshot` is a client-visible immutable snapshot metadata DTO for a bucket snapshot, including identity, status, UUID, paths, checkpoint directory, and referenced/exclusive size accounting.

### Important APIs and Types
The constructor stores volume, bucket, name, creation time, `SnapshotStatus`, `UUID`, snapshot path, checkpoint directory, referenced sizes, and exclusive sizes. `fromSnapshotInfo` converts OM `SnapshotInfo` and folds directory deep-cleaning deltas into exclusive sizes. It implements `equals`, `hashCode`, and `toString`.

### Control Flow
`fromSnapshotInfo` reads all fields from OM metadata and calls `getCheckpointDirName(0)`. Exclusive size getters represent base exclusive size plus deep-cleaning delta at conversion time.

### State and Persistence Behavior
The object is immutable and local-only. Snapshot metadata and size counters persist in OM and can change after this DTO is created, especially while deletion/deep-cleaning work progresses.

### Dependencies and Integration Points
It depends on `SnapshotInfo` and `SnapshotStatus` from OM helpers. It is returned by `ObjectStore.getSnapshotInfo` and `ObjectStore.listSnapshot`.

### Risks and Edge Cases
`getSnapshotStatus` returns the enum name as a string rather than the enum. `fromSnapshotInfo` hardcodes checkpoint directory index `0`. Equality includes all size fields, so two objects for the same snapshot can compare unequal if accounting changes.

### Test Signals
Tests should verify conversion from `SnapshotInfo`, inclusion of deep-cleaning deltas, equality/hash behavior, checkpoint directory selection, and status string compatibility.
