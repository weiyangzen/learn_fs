<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestStringToSignProducer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestStringToSignProducer.java

## Purpose
Tests Signature V4 canonical request and string-to-sign generation plus required header validation.

## Important APIs, types, and functions
Uses `StringToSignProducer.createSignatureBase`, `AuthorizationV4HeaderParser`, `SignatureInfo`, `LowerCaseKeyStringMap`, `HeaderPreprocessor.ORIGINAL_CONTENT_TYPE`, mocked `ContainerRequestContext`/`UriInfo`, `S3_AUTHINFO_CREATION_ERROR`, and SHA-256 hashing.

## Control flow
The main test constructs headers, fixes original content type, builds a known canonical request for `GET /buckets`, hashes it, and asserts the produced string-to-sign. Parameterized request-header validation covers missing/invalid/expired/future `X-Amz-Date` and missing `X-Amz-Content-Sha256`. Canonical-header validation covers missing `host`, missing signed `x-amz-security-token`, and signed headers absent from request headers.

## State and persistence behavior
No persistence. Header maps are normalized and may be adjusted by `fixContentType`; generated signature base depends on request URI, method, query parameters, credential scope, and canonical headers.

## Dependencies and integration points
This is core to S3 request authentication and depends on JAX-RS request context data and header preprocessing.

## Risks and edge cases
The tests cover simple URI/query cases, not complex percent encoding, duplicate query parameters, or multi-value signed headers.

## Test signals
Signals are exact string-to-sign equality and expected `S3_AUTHINFO_CREATION_ERROR` codes for invalid header/canonical-header cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/signature/TestStringToSignProducer.java -->
