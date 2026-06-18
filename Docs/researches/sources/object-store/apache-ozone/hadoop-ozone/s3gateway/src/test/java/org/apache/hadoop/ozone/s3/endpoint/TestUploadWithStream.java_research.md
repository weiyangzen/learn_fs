<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestUploadWithStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestUploadWithStream.java

## Purpose
Tests object upload through datastream-enabled S3 write paths.

## Important APIs, types, and functions
Uses `ObjectEndpointStreaming.put`, `ObjectEndpoint.isDatastreamEnabled`, `OZONE_FS_DATASTREAM_AUTO_THRESHOLD`, `HDDS_CONTAINER_RATIS_DATASTREAM_ENABLED`, `MultiDigestInputStream`, `FailingInputStream`, `AuditLogger.PerformanceStringBuilder`, and copy-source header handling.

## Control flow
Setup enables datastream and sets a one-byte auto threshold. Tests assert streaming is enabled, perform a normal PUT, directly invoke streaming PUT with a failing body and verify no key commit, and create a source stream key then copy it via `COPY_SOURCE_HEADER`.

## State and persistence behavior
Stub bucket state should contain keys only after successful uploads. A body read failure must leave no destination key. Copy via streaming path should persist a new key with the same data size as the source.

## Dependencies and integration points
This covers the S3 gateway streaming write implementation, Ozone datastream output, digest-wrapped input, conditional write parsing, and copy handling with streaming enabled.

## Risks and edge cases
The tests use stub streams and small content. They do not cover backpressure, large buffers, partial datanode failures, or checksum mismatch in datastream mode.

## Test signals
Signals are `isDatastreamEnabled`, successful PUT/copy, exact failure message `upload interrupted`, missing key after failure, and matching source/destination data sizes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestUploadWithStream.java -->
