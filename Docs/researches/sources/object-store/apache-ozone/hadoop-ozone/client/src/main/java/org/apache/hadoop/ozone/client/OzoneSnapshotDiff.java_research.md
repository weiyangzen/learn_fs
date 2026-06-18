## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneSnapshotDiff.java

### Purpose
`OzoneSnapshotDiff` is a small DTO representing one snapshot diff job for a bucket.

### Important APIs and Types
Fields include volume, bucket, from snapshot, to snapshot, and `SnapshotDiffResponse.JobStatus`. `fromSnapshotDiffJob` converts OM `SnapshotDiffJob` into the client DTO.

### Control Flow
There is no behavior beyond storing constructor values and converting from OM job fields.

### State and Persistence Behavior
The object is immutable and local. Job status is a snapshot of OM state at list time and may change as async diff jobs progress.

### Dependencies and Integration Points
It is used by `ObjectStore.listSnapshotDiffJobs` and maps from `SnapshotDiffJob`.

### Risks and Edge Cases
There is no equality/hash implementation, so list comparisons need field assertions. Status staleness is expected for async jobs.

### Test Signals
Tests should verify conversion from OM job, field getters, and iterator integration in `ObjectStore`.
