<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ObjectWriteGuard.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ObjectWriteGuard.java

## Purpose
Guarded copy/commit helper for S3 object writes. It tracks the number of bytes transferred, records transfer failures, and installs pre-commit checks on Ozone output streams.

## Important APIs, types, and functions
- Constructors accept `OzoneOutputStream` or generic `OutputStream`; the Ozone constructor registers pre-commit hooks immediately.
- `copyFrom` reads up to `expectedLength` into a bounded buffer and writes to the output stream.
- `validateBeforeCommit` rejects prior transfer failures and content-length mismatches.
- `addPreCommit` lets callers add MD5 and SHA-256 validators.
- `getMetadata` exposes `OzoneOutputStream` metadata for ETag and custom metadata mutation.

## Control flow
On construction the guard adds a content-length pre-commit hook. `copyFrom` loops until expected bytes are written or EOF occurs, recording read/write exceptions. `close` closes the stream, triggering Ozone pre-commit hooks before the write is committed.

## State and persistence behavior
The guard itself tracks in-memory `writtenLength` and `transferFailure`. Persistent commit happens only when the underlying output stream closes successfully with all pre-commit validators passing.

## Dependencies and integration points
Used by normal PUT, copy object, multipart part upload, and MPU part copy. Depends on `EndpointBase.validateContentLength`, `OzoneOutputStream.setPreCommits`, and Ratis `CheckedRunnable`.

## Risks and edge cases
The copy loop intentionally stops at `expectedLength`; extra bytes in the request body are not consumed here. EOF before expected length is detected at commit, not at read time. `getMetadata` assumes the generic stream is actually an `OzoneOutputStream` except in subclasses.

## Test signals
Tests should cover short body rejection, read/write exception propagation, custom pre-commit failures, metadata updates before close, and no commit after transfer failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ObjectWriteGuard.java -->
