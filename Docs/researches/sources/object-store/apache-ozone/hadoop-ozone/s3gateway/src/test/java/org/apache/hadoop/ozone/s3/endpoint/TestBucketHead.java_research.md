
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketHead.java

Purpose: tests HEAD bucket behavior through `BucketEndpoint`.

Important APIs and control flow: setup creates an S3 bucket and endpoint. Success test calls `head(bucketName)` and expects HTTP 200. Missing-bucket test catches `OS3Exception` and asserts S3 `NO_SUCH_BUCKET` code and message.

State, dependencies, integration: relies on `ObjectStoreStub`/`OzoneVolumeStub` bucket lookup and endpoint error mapping.

Risks and test signals: covers only existence status, not headers. Manual try/catch style means reaching the end without exception fails explicitly.
