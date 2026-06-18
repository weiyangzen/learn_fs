
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestBucketGetLocation.java

Purpose: tests `GET /{bucket}?location` behavior.

Important APIs and control flow: setup creates a stub bucket and sets query parameter `location`. The test asserts `bucketEndpoint.get(BUCKET_NAME)` returns S3 `NOT_IMPLEMENTED`.

State, dependencies, integration: minimal in-memory client state. Integrates bucket endpoint query dispatch for unsupported GetBucketLocation.

Risks and test signals: documents that bucket location is intentionally not implemented, so future support should update this test. Bucket name contains a space, which also lightly exercises name propagation.
