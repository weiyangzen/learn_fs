
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketDelete.java

Purpose: tests bucket delete behavior through `BucketEndpoint`.

Important APIs and control flow: setup creates stub client/object store and S3 bucket. `testBucketEndpoint` deletes the bucket and expects HTTP 204. `testDeleteWithNoSuchBucket` asserts S3 `NO_SUCH_BUCKET` code/message for missing bucket. `testDeleteWithBucketNotEmpty` creates a directory marker and asserts S3 `BUCKET_NOT_EMPTY`.

State, dependencies, integration: depends on `OzoneVolumeStub.deleteBucket` emptiness checks and `BucketEndpoint` OM-to-S3 error mapping.

Risks and test signals: tests use manual try/catch/fail rather than `assertThrows`, but they clearly protect error codes/messages. Bucket emptiness depends on stub `OzoneBucketStub.isEmpty`, which checks key metadata only.
