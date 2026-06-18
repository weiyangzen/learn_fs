<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectDelete.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectDelete.java

## Purpose
Minimal test for S3 object delete behavior.

## Important APIs, types, and functions
Uses `EndpointTestUtils.delete`, `EndpointTestUtils.assertStatus`, `ObjectEndpoint`, `OzoneClientStub`, `OzoneBucket.createKey`, and HTTP status `204 No Content`.

## Control flow
The test creates a stub S3 bucket, writes one zero-length key, builds an object endpoint, invokes delete, and verifies the bucket no longer lists any keys.

## State and persistence behavior
State is the in-memory key table in `OzoneClientStub`. Delete should remove the key and return a no-content S3 response.

## Dependencies and integration points
This covers `ObjectEndpoint.delete` integration with the Ozone bucket delete path and the S3 response status contract.

## Risks and edge cases
Only one success path is covered. Nonexistent keys, nonexistent buckets, versioned deletes, permission failures, and directory keys are tested elsewhere or not here.

## Test signals
Signals are HTTP 204 and an empty `bucket.listKeys("")` iterator after deletion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectDelete.java -->
