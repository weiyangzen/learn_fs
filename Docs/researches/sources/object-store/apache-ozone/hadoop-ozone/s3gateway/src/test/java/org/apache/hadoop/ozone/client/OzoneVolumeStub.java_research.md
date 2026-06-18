
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/OzoneVolumeStub.java

Purpose: in-memory `OzoneVolume` for tests, owning buckets and volume ACLs.

Important APIs and control flow: builder preserves fluent `OzoneVolume.Builder` methods. `createBucket` throws `BUCKET_ALREADY_EXISTS` on duplicate and creates `OzoneBucketStub` with default RATIS/THREE replication, bucket layout, storage type, versioning, and creation time. `getBucket` throws `BUCKET_NOT_FOUND` when absent. Bucket listing filters by prefix/previous marker and sorts by bucket name. `deleteBucket` removes only empty bucket stubs, otherwise throws `BUCKET_NOT_EMPTY`. ACL methods clone or mutate an in-memory list.

State, dependencies, integration: holds maps of bucket name to bucket and an ACL list. Used by `ObjectStoreStub` and bucket/ACL/list/delete tests.

Risks and test signals: state is not thread-safe. ACL cloning is shallow. Default replication and bucket args are simplified but enough for S3 endpoint behavior. `TestBucketDelete`, `TestBucketAcl`, and `TestBucketList` depend on this implementation.
