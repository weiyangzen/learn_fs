<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV2HeaderParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV2HeaderParser.java

## Purpose
Parser for legacy AWS Signature Version 2 `Authorization` headers.

## Important APIs, types, and functions
- `IDENTIFIER` is `AWS`.
- `parseSignature` accepts headers of form `AWS <accessKey>:<signature>`.
- Returns `SignatureInfo` with version `V2`, access key, and signature.

## Control flow
If the auth header is absent or does not start with `AWS `, it returns null. Otherwise it validates the two-token auth shape, the `accessKey:signature` shape, and nonblank access key/signature.

## State and persistence behavior
No state beyond the constructor-supplied header. No persistence.

## Dependencies and integration points
Used as the final parser fallback in `AWSSignatureProcessor`. The resulting `SignatureInfo` is later consumed by auth code.

## Risks and edge cases
Splitting on spaces and colons is strict; extra spaces or colon-containing signatures will be malformed. V2 canonical string generation is not in this file.

## Test signals
Tests should cover valid V2 auth, absent/non-V2 headers returning null, blank access key/signature, and malformed token counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV2HeaderParser.java -->
