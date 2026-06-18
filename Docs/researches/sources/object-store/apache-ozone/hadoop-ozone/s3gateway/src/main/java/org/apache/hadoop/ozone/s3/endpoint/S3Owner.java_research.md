<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Owner.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Owner.java

## Purpose
XML DTO and helper for S3 owner identity plus expected bucket-owner condition validation.

## Important APIs, types, and functions
- `DEFAULT_S3OWNER_ID` and `DEFAULT_S3_OWNER` provide canonical Ozone owner identity defaults.
- `of(String displayName)` creates owner DTOs using the default canonical ID and volume owner as display name.
- `hasBucketOwnershipVerificationConditions` detects expected destination/source owner headers.
- `verifyBucketOwnerCondition` and `verifyBucketOwnerConditionOnCopyOperation` enforce owner matches.

## Control flow
Verification reads the relevant header, skips empty headers or null actual owner, and throws `BUCKET_OWNER_MISMATCH` if the expected value differs from the actual owner.

## State and persistence behavior
No persistent state is modified. Owner values are serialized into list/ACL responses and used to gate operations.

## Dependencies and integration points
Used by root listing, object HEAD/PUT/copy/MPU operations, and ACL DTOs. Depends on `S3Consts.EXPECTED_BUCKET_OWNER_HEADER`, `S3Consts.EXPECTED_SOURCE_BUCKET_OWNER_HEADER`, and `S3ErrorTable`.

## Risks and edge cases
Ozone bucket owner strings are compared directly with expected S3 header values, so caller assumptions about canonical ID versus username matter. Copy operations may validate source and destination independently; callers pass nulls when a side was already checked.

## Test signals
Tests should assert matching owner pass-through, mismatched source/destination owner failures, empty header ignored, and correct response XML owner fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Owner.java -->
