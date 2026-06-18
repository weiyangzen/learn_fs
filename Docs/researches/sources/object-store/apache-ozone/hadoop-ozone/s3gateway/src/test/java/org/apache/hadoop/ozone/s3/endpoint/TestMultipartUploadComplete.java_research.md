<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultipartUploadComplete.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultipartUploadComplete.java

## Purpose
End-to-end unit tests for completing multipart uploads through the S3 object endpoint.

## Important APIs, types, and functions
Uses `EndpointTestUtils.initiateMultipartUpload`, `uploadPart`, `completeMultipartUpload`, `CompleteMultipartUploadRequest.Part`, `ObjectEndpoint.head`, and custom metadata headers with `CUSTOM_METADATA_HEADER_PREFIX`.

## Control flow
Setup creates an S3 bucket and object endpoint. The happy test initiates upload, uploads two parts, and completes. Metadata coverage initiates upload with custom metadata, uploads one part, completes, then checks `HEAD` response metadata. Error tests tamper with requested part order and ETag to assert `INVALID_PART_ORDER` and `INVALID_PART`.

## State and persistence behavior
Stub bucket state moves from pending multipart upload to a committed key after completion. Metadata attached at initiation must persist onto the final key. Invalid completion requests must not silently commit corrupted part lists.

## Dependencies and integration points
This covers `ObjectEndpoint.completeMultipartUpload`, Ozone multipart validation, response closing through `Response`, and metadata propagation from request headers to completed object metadata.

## Risks and edge cases
It does not read final object content, test missing upload IDs, duplicate parts, empty part completion behavior beyond metrics use, or minimum part-size constraints.

## Test signals
Signals are successful completion, custom metadata visible through `HEAD`, and exact S3 error codes for bad part ordering and wrong ETag.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultipartUploadComplete.java -->
