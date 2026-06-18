<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectMultiDelete.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectMultiDelete.java

## Purpose
Tests S3 multi-object delete execution and quiet-mode response shaping.

## Important APIs, types, and functions
Uses `BucketEndpoint.multiDelete`, `MultiDeleteRequest`, nested `DeleteObject`, `MultiDeleteResponse`, `OzoneClientStub`, and bucket key listing through `OzoneKey`.

## Control flow
`initTestData` creates a bucket with keys `key1`, `key2`, and `key3`. The normal test requests deletion of `key1`, `key2`, and missing `key4`, then checks only `key3` remains and deleted-object response entries are populated. The quiet test sets `quiet=true` and verifies the same bucket mutation but no deleted-object entries.

## State and persistence behavior
Deletes mutate the stub bucket key set. Missing keys are treated as deleted for S3-compatible idempotency in this test, and quiet mode only affects response contents, not deletion behavior.

## Dependencies and integration points
This verifies `BucketEndpoint.multiDelete` mapping from parsed request objects into Ozone `deleteKeys` behavior and S3 response assembly.

## Risks and edge cases
It does not cover per-key errors, access denied, malformed XML, version IDs, or very large delete batches.

## Test signals
Signals are final key set equality, deleted-object count, and error list count for both normal and quiet modes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectMultiDelete.java -->
