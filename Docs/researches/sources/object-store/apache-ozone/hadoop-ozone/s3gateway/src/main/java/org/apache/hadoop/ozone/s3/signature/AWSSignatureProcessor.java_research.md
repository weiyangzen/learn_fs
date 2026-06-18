<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AWSSignatureProcessor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AWSSignatureProcessor.java

## Purpose
Request-scoped signature processor that detects and parses AWS S3 authorization formats into `SignatureInfo`.

## Important APIs, types, and functions
- Implements `SignatureProcessor`.
- `parseSignature` tries V4 authorization header, V4 query parameters, then V2 authorization header.
- `LowerCaseKeyStringMap` normalizes request headers, combines duplicates, and restores original content type after header preprocessing.
- `buildAuthFailureMessage` creates S3 auth audit failure records.
- `setContext` supports tests.

## Control flow
Headers are copied to a lowercase map. Parser instances are tried in fixed priority order; malformed parser input is audited and returned as `AuthorizationHeaderMalformed`; null parser results mean "not this auth style". If nothing matches, version `NONE` is returned. The unfiltered request URI path is stored for canonical request construction.

## State and persistence behavior
Holds request context only for the request scope. No persistence.

## Dependencies and integration points
Used by authorization filters and request injection. Depends on JAX-RS `ContainerRequestContext`, `AuthorizationV4HeaderParser`, `AuthorizationV4QueryParser`, `AuthorizationV2HeaderParser`, audit logger, `AuditUtils`, and `HeaderPreprocessor`.

## Risks and edge cases
Parser priority matters when both header and query credentials exist. Duplicate headers are concatenated using only the first value from each map entry, which may diverge from canonical AWS behavior. Content-Type repair is required because header preprocessing can otherwise break signatures.

## Test signals
`TestAWSSignatureProcessor` and authorization filter tests should cover header/query/V2 detection, unsigned requests, malformed audit failures, lowercase lookup, duplicate header combining, and original content-type restoration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AWSSignatureProcessor.java -->
