<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/ContinueToken.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/ContinueToken.java

## Purpose
Encodes and decodes continuation tokens for paginated bucket/key listing using last key and optional last directory.

## Important APIs, types, and functions
- Constructor requires non-null `lastKey` and stores non-empty `lastDir`.
- `encodeToString` serializes key length, key bytes, optional dir bytes, hex-encodes them, and appends a SHA-256 digest separated by `-`.
- `decodeFromString` verifies separator and digest, decodes the hex payload, and reconstructs key/dir.
- `equals`, `hashCode`, and `toString` support tests and diagnostics.

## Control flow
Decoding rejects missing separators, digest mismatches, and bad hex with `InvalidArgument`, customizing the message for incorrect token payloads.

## State and persistence behavior
Tokens are client-visible serialized state but not server-persisted. They carry enough state to resume listing after the last returned entry.

## Dependencies and integration points
Used by root directory bucket listing and list-object responses. Depends on Commons Codec Hex/DigestUtils and `S3ErrorTable`.

## Risks and edge cases
The digest is integrity protection, not a secret or signature. `hashCode` only uses `lastKey` while `equals` also uses `lastDir`. Decoding accepts any remaining bytes as `lastDir`, including empty string.

## Test signals
`TestContinueToken` covers round-trip, Unicode keys/dirs, null dirs, and invalid token errors. Pagination tests should verify decoded `lastKey` resumes iteration correctly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/ContinueToken.java -->
