<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV4HeaderParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV4HeaderParser.java

## Purpose
Parser and validator for AWS Signature Version 4 authorization headers.

## Important APIs, types, and functions
- `parseSignature` parses `AWS4-HMAC-SHA256 Credential=..., SignedHeaders=..., Signature=...`.
- `parseAlgorithm` enforces `AWS4-HMAC-SHA256`.
- `parseCredentials` builds and validates `Credential`.
- `parseSignedHeaders` validates non-empty signed header list.
- `parseSignature` validates non-empty hex signature.
- `validateDateRange` allows credential dates from yesterday through tomorrow.

## Control flow
Non-AWS4 headers return null. AWS4 headers must contain a space separating algorithm and attributes, exactly three comma-separated attributes, valid credential scope, signed headers, and hex signature. Date range and format failures are reported as `MalformedResourceException` carrying the full header as resource.

## State and persistence behavior
Stores only constructor-supplied auth/date headers. No persistence.

## Dependencies and integration points
Used by `AWSSignatureProcessor`. Depends on `Credential`, `SignatureInfo`, `SignatureProcessor.DATE_FORMATTER`, Apache Commons Hex decoding, and Hadoop string collection parsing.

## Risks and edge cases
The parser is strict about attribute order and count. It validates credential date but uses the `x-amz-date` header as `dateTime` without checking it here; canonical request validation handles timestamp range later. Credential service is not limited to `s3`, which enables S3 Express service scopes.

## Test signals
`TestAuthorizationV4HeaderParser` should cover valid parsing, missing fields, invalid algorithm, non-hex signatures, empty signed headers, invalid credential segments, and date range limits.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV4HeaderParser.java -->
