<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV4QueryParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV4QueryParser.java

## Purpose
Parser and validator for SigV4 presigned URL query parameters.

## Important APIs, types, and functions
- `parseSignature` requires `X-Amz-Signature` and returns version `V4` with `signPayload=false`.
- `validateAlgorithm` enforces `AWS4-HMAC-SHA256`.
- `validateDateAndExpires` enforces `X-Amz-Date`, `X-Amz-Expires`, 1 to 604800 seconds, and not expired.
- `validateCredential`, `validateSignedHeaders`, and `validateSignature` validate credential scope, signed headers, and hex signature.

## Control flow
If no `X-Amz-Signature` is present, returns null. Otherwise it validates algorithm, date/expiry, URL-decodes credential, validates credential fields and date, signed headers, and signature before building `SignatureInfo`.

## State and persistence behavior
Stores query parameter map only. No persistence.

## Dependencies and integration points
Used by `AWSSignatureProcessor` for presigned requests. Depends on `Credential`, `StringToSignProducer.TIME_FORMATTER`, `S3Utils.urlDecode`, and Commons Hex decoding.

## Risks and edge cases
`X-Amz-Expires` is parsed with `Long.parseLong`; nonnumeric values can throw outside the declared `DateTimeParseException` catch in `parseSignature`. Query parameters are single-valued by prior conversion, so repeated params lose all but the first value. Expiry uses local current time at parse time.

## Test signals
Tests should cover valid presigned URLs, missing algorithm/date/expires/signed headers, expired URLs, out-of-range expiry, invalid credential URL encoding, non-hex signature, and nonnumeric expires.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV4QueryParser.java -->
