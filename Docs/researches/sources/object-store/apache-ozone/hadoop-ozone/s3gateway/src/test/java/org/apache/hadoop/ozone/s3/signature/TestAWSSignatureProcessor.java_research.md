<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAWSSignatureProcessor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAWSSignatureProcessor.java

## Purpose
Tests case-insensitive key behavior in the signature processor's lower-case header map.

## Important APIs, types, and functions
Uses `AWSSignatureProcessor.LowerCaseKeyStringMap.put`, `remove`, and `containsKey`.

## Control flow
The test inserts an `Authorization` header, removes it with uppercase `AUTHORIZATION`, and asserts the value is returned and lowercase lookup no longer exists.

## State and persistence behavior
State is an in-memory map normalized for HTTP header names. No persistence.

## Dependencies and integration points
Signature parsing and canonical request construction depend on case-insensitive header lookup/removal, especially for `Authorization`.

## Risks and edge cases
Only removal is tested; iteration order, duplicate puts, and mixed-case contains/get behavior are not covered here.

## Test signals
Passing means header removal is case-insensitive and removes the normalized entry.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAWSSignatureProcessor.java -->
