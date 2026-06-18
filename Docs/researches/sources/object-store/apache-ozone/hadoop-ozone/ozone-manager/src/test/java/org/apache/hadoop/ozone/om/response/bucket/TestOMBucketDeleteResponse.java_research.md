# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/bucket/TestOMBucketDeleteResponse.java

Purpose: Verifies `OMBucketDeleteResponse` removes a bucket entry when combined with a prior create response in the same batch.

Important APIs/types/functions: Uses `OMBucketCreateResponse`, `OMBucketDeleteResponse`, protobuf `CreateBucketResponse`, `DeleteBucketResponse`, `OMResponse`, `OmBucketInfo`, and `bucketTable`.

Control flow: The test builds bucket metadata, creates successful create and delete response objects, calls both `addToDBBatch` methods on the same batch, commits, and then reads the bucket table by computed bucket key.

State/persistence: The create write and delete write are committed atomically through one batch. Final persistent state is absence of the bucket row.

Dependencies/integration: Tests response composition and table delete behavior through the OM metadata manager. It reuses the common bucket-info helper.

Risks/test signals: This does not test deleting a nonexistent bucket or error responses. The main signal is that delete operations in a batch override a preceding create for the same key.
