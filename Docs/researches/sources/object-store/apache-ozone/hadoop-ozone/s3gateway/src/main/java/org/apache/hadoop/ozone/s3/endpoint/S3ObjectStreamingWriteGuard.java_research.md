<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ObjectStreamingWriteGuard.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ObjectStreamingWriteGuard.java

## Purpose
Datastream-specific write guard that adapts `S3ObjectWriteGuard` to `OzoneDataStreamOutput`.

## Important APIs, types, and functions
- Constructor registers inherited pre-commit checks with `OzoneDataStreamOutput`.
- Overrides `write` to send a `ByteBuffer` to datastream output.
- Overrides `getMetadata` through `KeyMetadataAware`.
- Overrides `close` to close the datastream output.

## Control flow
The inherited copy loop tracks bytes and transfer failures. This subclass changes only the sink operation and metadata access path.

## State and persistence behavior
Persistent object or MPU data is committed by `OzoneDataStreamOutput.close` after registered pre-commit hooks pass. Metadata is mutated through the datastream output's key metadata map before close.

## Dependencies and integration points
Used by `ObjectEndpointStreaming` for datastream PUT, copy, and multipart part writes. Depends on `OzoneDataStreamOutput` and `KeyMetadataAware`.

## Risks and edge cases
If a datastream output implementation stops implementing `KeyMetadataAware`, ETag/tag metadata writes fail at runtime. ByteBuffer wrapping must preserve offset and length correctly for partial buffer writes.

## Test signals
Datastream tests should assert content length validation, close-time pre-commit failure behavior, ETag metadata persistence, and correct byte counts for non-zero offsets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ObjectStreamingWriteGuard.java -->
