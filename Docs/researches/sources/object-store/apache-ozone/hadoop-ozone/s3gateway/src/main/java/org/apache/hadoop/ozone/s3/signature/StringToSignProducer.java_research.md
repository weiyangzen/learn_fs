<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/StringToSignProducer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/StringToSignProducer.java

## Purpose
Utility for building SigV4 canonical requests and strings-to-sign for Ozone S3 authorization.

## Important APIs, types, and functions
- `createSignatureBase` builds the SigV4 string-to-sign from `SignatureInfo`, request method, URI, headers, and query parameters.
- `buildCanonicalRequest` canonicalizes URI, query string, signed headers, and payload hash.
- `hash` computes SHA-256 hex.
- `fromMultiValueToSingleValueMap` converts query params to first-value map.
- `validateSignedHeader` checks host/date/content-sha headers.
- `validateCanonicalHeaders` requires host and all `x-amz-*` headers except `x-amz-content-sha256` to be signed.

## Control flow
The string-to-sign is algorithm, request timestamp, credential scope, and hash of canonical request. Canonical request encodes each URI path segment, sorts query parameters except `X-Amz-Signature`, renders signed headers in supplied order, validates signed header presence and timestamp range, and uses `UNSIGNED-PAYLOAD` for presigned requests or the `x-amz-content-sha256` header for signed-payload requests.

## State and persistence behavior
Stateless utility. No persistence.

## Dependencies and integration points
Used by the authorization filter after signature parsing. Depends on `SignatureInfo`, lowercased header maps, `S3Utils.urlEncode`, `S3Consts` payload constants, and S3 auth error creation.

## Risks and edge cases
Canonicalization is security-sensitive. Query parameters are single-valued, header whitespace is not normalized beyond stored values, and signed headers are used in caller-provided order. Missing host or unsigned `x-amz-*` headers fail auth. V4 header signing requires `x-amz-content-sha256`; presigned URLs force unsigned payload.

## Test signals
Authorization tests should use AWS canonical examples, query sorting/encoding cases, path encoding with slash preservation, missing signed headers, timestamp range failures, unsigned payload, and streaming payload constants.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/StringToSignProducer.java -->
