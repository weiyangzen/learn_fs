<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV4HeaderParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV4HeaderParser.java

## Purpose
Tests AWS Signature V4 `Authorization` header parsing and validation.

## Important APIs, types, and functions
Uses `AuthorizationV4HeaderParser.parseSignature`, `SignatureInfo`, `Credential`, `SignatureProcessor.DATE_FORMATTER`, and `MalformedResourceException`.

## Control flow
The suite parses well-formed headers, headers without spaces after commas, and headers with current/yesterday/tomorrow credential dates. Failure tests cover missing header parts, invalid credentials, date outside accepted range or wrong format, empty region/service/request segments, invalid request suffix, invalid signed headers, invalid/empty signatures, invalid algorithms, unsupported non-AWS4 schemes returning null, and malformed credential keys.

## State and persistence behavior
No persistence. Parser state is derived from header string and request date. Date validation depends on current local date through `LocalDate.now()`.

## Dependencies and integration points
This feeds S3 authentication, signature canonicalization, and credential-scope region/service extraction used elsewhere such as S3 Express directory bucket region handling.

## Risks and edge cases
Tests are date-relative and can be sensitive near midnight or timezone differences. They assert parser-level validation, not cryptographic signature verification.

## Test signals
Signals are exact `SignatureInfo` field values for valid headers, null for unsupported schemes, and `MalformedResourceException` for invalid V4 shapes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestAuthorizationV4HeaderParser.java -->
