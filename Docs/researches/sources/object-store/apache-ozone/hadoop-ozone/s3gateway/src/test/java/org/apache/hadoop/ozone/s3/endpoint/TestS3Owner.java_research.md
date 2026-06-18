<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestS3Owner.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestS3Owner.java

## Purpose
Unit tests expected bucket owner validation for normal and copy operations.

## Important APIs, types, and functions
Exercises `S3Owner.hasBucketOwnershipVerificationConditions`, `verifyBucketOwnerCondition`, `verifyBucketOwnerConditionOnCopyOperation`, headers `EXPECTED_BUCKET_OWNER_HEADER` and `EXPECTED_SOURCE_BUCKET_OWNER_HEADER`, and error `BUCKET_OWNER_MISMATCH`.

## Control flow
Parameterized tests check when owner verification is enabled based on non-empty headers. Null headers and null server owner IDs are allowed. Direct bucket validation succeeds on matching owner and fails on mismatch. Copy validation checks source and destination owners independently and verifies the failing resource is the source or destination bucket.

## State and persistence behavior
No persistence. The state is request header values and server-known owner strings used to gate operations.

## Dependencies and integration points
These helpers are used by object and copy endpoints to implement AWS expected-owner guard headers.

## Risks and edge cases
The tests do not exercise full endpoint flows or real owner lookup. Empty-string handling is covered, but whitespace-only values are not.

## Test signals
Signals are boolean condition detection, absence of exceptions for disabled checks, and `OS3Exception` message/resource for owner mismatches.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestS3Owner.java -->
