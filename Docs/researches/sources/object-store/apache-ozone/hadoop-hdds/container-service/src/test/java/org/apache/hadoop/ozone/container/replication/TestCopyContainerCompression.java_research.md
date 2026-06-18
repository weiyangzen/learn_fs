## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestCopyContainerCompression.java

Purpose: Validates the `CopyContainerCompression` enum's protobuf conversion, configuration binding, fallback behavior, and stream wrapping round trip.

Important APIs/types/functions: `CopyContainerCompression.toProto`, `fromProto`, `setOn`, `getConf`, `getDefaultCompression`, `wrap(OutputStream)`, `wrap(InputStream)`, and config key `HDDS_CONTAINER_REPLICATION_COMPRESSION`.

Control flow: Parameterized enum tests assert conversion and config round trip for every compression value. Invalid config string returns the default. I/O test writes random bytes through compression output, checks compressed bytes differ for compression modes, then reads through the matching input wrapper and verifies full restoration.

State and persistence behavior: Uses byte-array streams only; no persisted files.

Dependencies and integration points: Shared by copy/download and send/upload replication streams to negotiate compression consistently with protobuf and `OzoneConfiguration`.

Risks and test signals: Good compatibility signal for new enum values. Small 16-byte payloads may not expose buffering edge cases for every compression codec.
