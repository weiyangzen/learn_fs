<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultipartUploadWithCopy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultipartUploadWithCopy.java

## Purpose
Tests multipart upload where individual parts are created by copying existing object data, including range copy and conditional timestamp headers.

## Important APIs, types, and functions
Uses `ObjectEndpoint.put` as UploadPart/UploadPartCopy, `COPY_SOURCE_HEADER`, `COPY_SOURCE_HEADER_RANGE`, `COPY_SOURCE_IF_MODIFIED_SINCE`, `COPY_SOURCE_IF_UNMODIFIED_SINCE`, `CopyPartResult`, `CompleteMultipartUploadRequest.Part`, and `OzoneMultipartUploadPartListParts`.

## Control flow
`@BeforeAll` creates a source key with a known ETag and derives before/after/future timestamp strings. The main multipart test uploads one normal part, full-copy and range-copy parts, and a copy with timestamp preconditions, then completes and reads final content. `testMultipartTSHeaders` iterates an enum of modified/unmodified-since combinations to assert which combinations should fail with `PreconditionFailed`. A final test confirms range-copy part size is the copied byte range length.

## State and persistence behavior
Source key data remains unchanged. Pending multipart state accumulates copied part data and metadata until completion commits the destination key. Range copy must persist a part with content length equal to the selected range.

## Dependencies and integration points
This integrates object copy, RFC-style timestamp parsing, multipart part registration, final completion, and Ozone stub key reads.

## Risks and edge cases
The timestamp matrix is time-sensitive and sleeps to avoid future-time ambiguity. It does not cover ETag preconditions for copy part or cross-bucket owner checks.

## Test signals
Signals include final concatenated object content, copy-part ETag/last-modified fields, expected `PRECOND_FAILED` codes, and persisted copied part size of four bytes for `bytes=0-3`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultipartUploadWithCopy.java -->
