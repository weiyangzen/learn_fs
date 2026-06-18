# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketDeleteRequestWithFSO.java

Extends bucket delete coverage for `FILE_SYSTEM_OPTIMIZED` buckets. The single FSO-specific test creates a delete request, seeds an FSO bucket, calls `validateAndUpdateCache`, verifies the bucket row is removed, and checks `omMetrics.getNumFSOBucketDeletes` increments from 0 to 1.

The local `createDeleteBucketRequest` builds the `DeleteBucketRequest` protobuf. State behavior is focused on `bucketTable` deletion under `getBucketKey(volume, bucket)` and metrics classification for FSO layout. Dependencies are superclass delete tests, `OMRequestTestUtils.addVolumeAndBucketToDB` with `BucketLayout.FILE_SYSTEM_OPTIMIZED`, and OM response handling.

Risk coverage is narrow but important: layout-aware bucket delete accounting. It does not seed FSO directory/key children, so non-empty tree behavior is not covered here. Signals are null bucket table row and exactly one FSO delete metric.
