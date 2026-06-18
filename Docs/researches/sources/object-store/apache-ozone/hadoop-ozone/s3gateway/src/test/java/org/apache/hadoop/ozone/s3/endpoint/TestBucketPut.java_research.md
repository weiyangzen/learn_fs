
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketPut.java

Purpose: tests S3 bucket creation through `BucketEndpoint.put`.

Important APIs and control flow: setup builds endpoint on a stub client. Test creates a bucket, expects HTTP 200 and non-null `Location`, then tries to create the same bucket again and expects S3 `BUCKET_ALREADY_EXISTS`.

State, dependencies, integration: uses `ObjectStoreStub.createS3Bucket` and `OzoneVolumeStub.createBucket` duplicate detection. Endpoint maps duplicate OM exception to S3 error.

Risks and test signals: covers duplicate behavior but not invalid bucket names, ACLs on create, or location constraints. Protects response location presence.
