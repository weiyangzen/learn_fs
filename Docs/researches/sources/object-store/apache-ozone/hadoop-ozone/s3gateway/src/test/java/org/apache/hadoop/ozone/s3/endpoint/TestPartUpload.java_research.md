<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestPartUpload.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestPartUpload.java

## Purpose
Tests S3 multipart `UploadPart` for regular and datastream-enabled paths.

## Important APIs, types, and functions
Parameterized class runs with `HDDS_CONTAINER_RATIS_DATASTREAM_ENABLED` false and true. It uses `EndpointTestUtils.put`, `initiateMultipartUpload`, `OzoneMultipartUploadPartListParts`, `S3StorageType`, `DECODED_CONTENT_LENGTH_HEADER`, `Content-MD5`, `EndpointBase` digest providers, and `FailingInputStream`.

## Control flow
Setup creates a bucket, endpoint, and config, then asserts datastream mode. Tests upload a part, replace the same part and require a changed ETag, accept `STANDARD_IA`, reject wrong upload IDs, reject incomplete bodies without recording parts, handle signed-chunk decoded length, reset MD5/SHA-256 digests after read failure, and validate Content-MD5 success and bad/invalid digest failures.

## State and persistence behavior
Part state remains under the pending upload ID. Uploading the same part number overwrites previous part metadata. Failed body reads and checksum failures must not persist a part. Digest instances are reset for future requests.

## Dependencies and integration points
This covers upload-part request query parameters, Ozone multipart part storage, datastream configuration, checksum validation, signed payload decoding, and storage-class handling.

## Risks and edge cases
It does not complete uploads, test very large parts, or exercise concurrent part replacement.

## Test signals
Signals include ETag presence/change, persisted part size, zero parts after failure, specific S3 error codes, and digest `reset()` calls in exception paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestPartUpload.java -->
