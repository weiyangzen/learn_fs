<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestContinueToken.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestContinueToken.java

## Purpose
Tests round-trip encoding/decoding of S3 continuation tokens.

## Important APIs, types, and functions
Uses `ContinueToken`, `encodeToString`, `decodeFromString`, `equals`, and `OS3Exception`.

## Control flow
Four tests create tokens with key plus directory, non-English key with null directory, non-English key and directory, and key with null directory. Each encodes to a string, decodes, and asserts equality with the original token.

## State and persistence behavior
No persistent state. Token contents must be serialized in a reversible form, including null directory values and non-ASCII characters.

## Dependencies and integration points
Continuation tokens are used by S3 list operations to resume pagination without exposing raw internal cursor structure.

## Risks and edge cases
The tests do not cover invalid token strings, tampering, empty key values, or compatibility with older token formats.

## Test signals
Passing means encoded tokens round-trip exactly for ASCII, non-English, and null-directory cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestContinueToken.java -->
