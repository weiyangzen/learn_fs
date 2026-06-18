<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureInfo.java

## Purpose
Request-scoped holder for parsed signature metadata used by authorization and string-to-sign creation.

## Important APIs, types, and functions
- Fields include version, date, dateTime, access ID, signature, signed headers, credential scope, algorithm, sign-payload flag, unfiltered URI, and string-to-sign.
- `initialize(SignatureInfo)` copies another instance, supporting injection/proxy patterns.
- `Version` enum has `NONE`, `V4`, and `V2`.
- Builder constructs immutable-style instances, though the outer object remains mutable for URI/string-to-sign.

## Control flow
Parsers build a `SignatureInfo`; `AWSSignatureProcessor` fills unfiltered URI; authorization code may create and store string-to-sign.

## State and persistence behavior
Request-scoped in-memory state. No persistence.

## Dependencies and integration points
Consumed by `StringToSignProducer`, authorization filters, root endpoint S3 Express detection, and endpoint logic that needs `isSignPayload`.

## Risks and edge cases
Default builder field values are empty strings, which can mask missing values until later validation. Mutability via `setUnfilteredURI` and `setStrToSign` means request scope must be respected.

## Test signals
Tests should assert parser-populated fields, request-scope copying through `initialize`, sign-payload differences between header and query signatures, and S3 Express credential-scope visibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureInfo.java -->
