<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestListParts.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestListParts.java

## Purpose
Validates S3 ListParts behavior for in-progress multipart uploads.

## Important APIs, types, and functions
The class uses `EndpointTestUtils.initiateMultipartUpload`, `uploadPart`, `listParts`, `ListPartsResponse`, `OzoneClientStub`, and S3 error `NO_SUCH_UPLOAD`.

## Control flow
Setup creates a bucket, starts one multipart upload, and uploads three numbered parts. `testListParts` requests all three parts and checks non-truncation. `testListPartsContinuation` requests two, uses the returned next part marker, and verifies the final page has one part. Unknown upload ID/key produces an S3 error.

## State and persistence behavior
Multipart part state is stored in the stub bucket under upload ID. Listing must expose ordered part metadata and preserve the continuation marker contract without completing or mutating the upload.

## Dependencies and integration points
This protects `ObjectEndpoint.listParts` and Ozone bucket `listParts` integration, including query-parameter conversion for `max-parts` and `part-number-marker`.

## Risks and edge cases
It does not inspect individual part ETags, timestamps, sizes, owner fields, or boundary values such as zero max parts.

## Test signals
Signals are `getTruncated`, list size, next marker behavior, and `NO_SUCH_UPLOAD` translation for unknown uploads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestListParts.java -->
