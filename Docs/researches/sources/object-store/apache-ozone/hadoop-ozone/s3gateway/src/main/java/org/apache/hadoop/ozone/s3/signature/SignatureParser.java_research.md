<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureParser.java

## Purpose
Small parser contract for extracting signature information from one authorization mechanism.

## Important APIs, types, and functions
- Constant `AUTHORIZATION_HEADER`.
- `parseSignature` returns `SignatureInfo`, null for nonmatching auth style, or throws `MalformedResourceException` for malformed recognized input.

## Control flow
`AWSSignatureProcessor` calls multiple implementations in priority order using the null-versus-exception distinction.

## State and persistence behavior
Interface only; no state or persistence.

## Dependencies and integration points
Implemented by V2 header, V4 header, and V4 query parsers.

## Risks and edge cases
Implementations must return null only when the auth style is absent, not when it is present but invalid, or malformed credentials may fall through to weaker/other auth modes.

## Test signals
Processor tests should ensure each parser obeys null and exception semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureParser.java -->
