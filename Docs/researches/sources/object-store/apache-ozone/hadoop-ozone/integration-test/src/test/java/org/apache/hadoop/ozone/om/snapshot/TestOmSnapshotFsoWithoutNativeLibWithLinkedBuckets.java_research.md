# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotFsoWithoutNativeLibWithLinkedBuckets.java

Purpose: This subclass runs the shared `TestOmSnapshot` suite for FSO buckets with native diff disabled and linked bucket creation enabled. It targets source-bucket resolution and linked-bucket snapshot semantics.

Important APIs/types/functions: The class extends `TestOmSnapshot`, uses `BucketLayout.FILE_SYSTEM_OPTIMIZED`, and calls `super(FILE_SYSTEM_OPTIMIZED, false, false, true, true)`.

Control flow: All test execution is inherited. The key constructor difference is `createLinkedBucket=true`, causing `TestOmSnapshot.createBucket` and initial bucket setup to create source buckets plus linked buckets and to maintain a link-to-source map for assertions and OM key resolution.

State and persistence behavior: Snapshot table keys, bucket names returned by snapshot info, and OM key lookups are expected to refer to the source bucket where appropriate. The inherited suite validates that snapshot operations through the linked bucket preserve point-in-time data and resolve to the correct underlying bucket.

Dependencies and integration points: This subclass depends on `TestDataUtil.createLinkedBucket`, linked bucket metadata, FSO key/file tables, and the non-native diff path. It integrates link resolution with snapshot create/delete/diff/list behavior.

Risks and edge cases: Linked bucket tests are prone to mismatches between visible bucket name and source bucket name, especially in snapshot table keys and `OzoneSnapshot.getBucketName`. Since native diff is disabled, this subclass does not cover linked buckets with native SST diff.

Test signals: Inherited assertions pass while using linked bucket mappings for snapshot info, key lookups, bucket deletion, quota handling, and diff outputs.
