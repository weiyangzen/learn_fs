<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestInitiateMultipartUpload.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestInitiateMultipartUpload.java

## Purpose
Verifies S3 multipart-upload initialization through `ObjectEndpoint.initializeMultipartUpload`.

## Important APIs, types, and functions
Uses `EndpointTestUtils.initiateMultipartUpload`, `EndpointBuilder.newObjectEndpointBuilder`, `OzoneClientStub`, `OzoneConsts.S3_BUCKET`, `OzoneConsts.KEY`, mocked `HttpHeaders`, `STORAGE_CLASS_HEADER`, and `ECReplicationConfig`.

## Control flow
The normal test creates an S3 bucket in the stub client, builds an object endpoint, initiates upload twice for the same bucket/key, and asserts different upload IDs. The EC test sets an EC replication config on the bucket and verifies initiation does not reject EC-backed keys.

## State and persistence behavior
State is held in `OzoneClientStub`: S3 bucket metadata and pending multipart upload records. Upload IDs must be unique per initiation and must capture bucket replication settings without committing object data.

## Dependencies and integration points
This is the entry point for later `put` part and complete calls. It integrates storage-class header parsing, bucket replication defaults, and Ozone multipart initiation.

## Risks and edge cases
The tests do not assert response XML fields beyond upload ID uniqueness, nor invalid buckets, storage classes, owner conditions, or metadata headers.

## Test signals
Passing means repeated initiation returns distinct IDs and EC bucket defaults are accepted.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestInitiateMultipartUpload.java -->
