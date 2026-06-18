<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV4QueryParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV4QueryParser.java

## Purpose
Tests AWS Signature V4 presigned URL query parameter parsing and canonical string generation.

## Important APIs, types, and functions
Uses `AuthorizationV4QueryParser.parseSignature`, `StringToSignProducer.createSignatureBase`, `AWSSignatureProcessor.LowerCaseKeyStringMap`, SHA-256 `MessageDigest`, and `MalformedResourceException`.

## Control flow
Validation tests mutate a parameter map to cover missing/empty/invalid algorithm, date, expires, credential, signed headers, and signature. Expiry bounds cover invalid zero, more than seven days, and expired requests. A valid unexpired parameter set must parse. The AWS example test overrides date validation, parses credentials, sets URI/header state, builds the canonical request hash, and asserts the string-to-sign matches the expected form.

## State and persistence behavior
No persistent state. Query parser output captures access ID, date, region, service, signed headers, and signature. Validation depends on current timestamp for expiry checks.

## Dependencies and integration points
This protects presigned URL authentication and canonical request construction for S3 gateway requests.

## Risks and edge cases
Date-relative tests can be time-sensitive. The invalid credential section starts with an invalid algorithm in the map, so some failures may be caught before credential validation.

## Test signals
Signals are exceptions for malformed query auth, successful parse for unexpired headers, and exact AWS-style string-to-sign equality.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV4QueryParser.java -->
