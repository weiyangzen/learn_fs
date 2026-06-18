<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureProcessor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureProcessor.java

## Purpose
Top-level contract for request signature processing plus shared signature constants.

## Important APIs, types, and functions
- Constants include content-type/content-md5 names, AWS4 signing algorithm, host header, and SigV4 date formatter.
- `parseSignature` returns a `SignatureInfo` or throws `OS3Exception`.

## Control flow
Implemented by `AWSSignatureProcessor`, which provides the request-scoped parser orchestration.

## State and persistence behavior
Interface only; no state or persistence.

## Dependencies and integration points
Used by authorization filters and signature parser classes for shared constants.

## Risks and edge cases
Changing constants affects all signature parsing and canonical request generation. Date formatter must remain `yyyyMMdd` for credential scopes.

## Test signals
Signature parser tests indirectly pin these constants through valid AWS examples.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureProcessor.java -->
