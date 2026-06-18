<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV2HeaderParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV2HeaderParser.java

## Purpose
Tests parsing of AWS Signature V2 authorization headers.

## Important APIs, types, and functions
Exercises `AuthorizationV2HeaderParser.parseSignature`, `SignatureInfo.getAwsAccessId`, `SignatureInfo.getSignature`, and `MalformedResourceException`.

## Control flow
The valid test parses `AWS accessKey:signature`. Invalid tests cover a non-AWS prefix returning null and malformed AWS headers with empty access key, empty signature, or missing signature throwing `MalformedResourceException`.

## State and persistence behavior
No persistent state. Parser output is a `SignatureInfo` object or null for unsupported algorithms.

## Dependencies and integration points
This is part of the S3 authentication filter path for legacy V2 signatures.

## Risks and edge cases
It does not cover access keys containing colons, whitespace variants, or canonical string generation.

## Test signals
Signals are parsed access key/signature values, null for unrelated scheme, and exceptions for malformed V2 headers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV2HeaderParser.java -->
