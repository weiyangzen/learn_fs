
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestAbortMultipartUpload.java

Purpose: tests aborting multipart uploads through `ObjectEndpoint`.

Important APIs and control flow: creates stub client and S3 bucket, sets `x-amz-storage-class` to `STANDARD`, builds object endpoint, initiates multipart upload, aborts it and expects HTTP 204, then aborts with a random upload ID and expects S3 `NO_SUCH_UPLOAD`.

State, dependencies, integration: uses in-memory multipart state in `OzoneBucketStub` through `EndpointTestUtils`. Integration covers object endpoint query-param dispatch to multipart abort.

Risks and test signals: only aborts before any parts are uploaded and does not verify cleanup of part maps. It protects the HTTP status and missing-upload error mapping.
