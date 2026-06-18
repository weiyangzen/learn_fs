<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestS3ObjectWriteGuard.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestS3ObjectWriteGuard.java

## Purpose
Tests close-time commit guards that prevent S3 object writes from committing after failed input reads, failed writes, or content-length mismatches.

## Important APIs, types, and functions
Uses `S3ObjectWriteGuard`, `S3ObjectStreamingWriteGuard`, `OzoneOutputStream`, `OzoneDataStreamOutput`, `KeyMetadataAwareOutputStream`, `KeyMetadataAwareByteBufferStreamOutput`, and reflection over `writtenLength`.

## Control flow
Tests inject `IOException` and runtime exceptions from input reads and assert close fails with the original cause. A failing output stream verifies write failures do not advance written length. Early EOF copies fewer bytes and then fails content-length validation with `OS3Exception`. The datastream variant injects a ByteBuffer write failure and checks close blocking.

## State and persistence behavior
The guard tracks copied/written length and first transfer failure. Once a transfer fails, close must not commit the underlying key stream; instead it throws a commit-blocking exception with the original cause.

## Dependencies and integration points
This protects object PUT and UploadPart write paths, including streaming/datastream output wrappers from `OzoneBucketStub`.

## Risks and edge cases
The test uses test stub streams rather than real datanode streams. Reflection makes it sensitive to private field renaming.

## Test signals
Signals include exact propagated failures, blocked close message, preserved cause, zero written length after output failure, early EOF validation text, and write attempt counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestS3ObjectWriteGuard.java -->
