# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketDeleteRequest.java

Tests `OMBucketDeleteRequest` for preExecute user-info mutation, successful bucket removal, missing-bucket failure, and delete protection when incomplete multipart uploads exist.

`createDeleteBucketRequest` builds `DeleteBucketRequest` in an `OMRequest`. The success test seeds volume and bucket rows with `OMRequestTestUtils.addVolumeAndBucketToDB`, calls `validateAndUpdateCache`, and expects the bucket table row to be null. The failure test validates without seed state and expects `BUCKET_NOT_FOUND`. The MPU test creates an `OmKeyInfo`, `OmMultipartKeyInfo`, and multipart info row using `OMMultipartUploadUtils` and `OMRequestTestUtils`, then verifies delete fails with `BUCKET_NOT_EMPTY` until the multipart entry is removed from cache and DB.

Persistence behavior includes deletion from `bucketTable` and presence/absence in `multipartInfoTable`. When MPUs exist, bucket metadata remains; after MPU cleanup, deletion succeeds. Dependencies include cache key/value APIs, HDDS replication protos, multipart helpers, `Time`, and OM response protobuf statuses.

Risks covered are accidental bucket deletion with incomplete MPUs and stale cache/table visibility during retry. Signals are changed request on preExecute, null bucket row on success, retained bucket row on `BUCKET_NOT_EMPTY`, `BUCKET_NOT_FOUND` for absent bucket, and final `Status.OK` after MPU deletion.
