
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestUnsignedChunkInputStream.java

Purpose: tests decoding of unsigned AWS chunked upload bodies by `UnsignedChunkInputStream`.

Important APIs and control flow: mirrors signed chunk tests for empty, trailer, missing terminator, single chunk, and multiple chunk cases. Assertions use full string read, full buffer read, and partial buffer read to ensure read APIs all return only decoded payload bytes.

State, dependencies, integration: no persistent state; uses byte-array input and UTF-8. Relevant to `STREAMING-UNSIGNED-PAYLOAD-TRAILER` and unsigned streaming upload paths.

Risks and test signals: covers framing and trailer tolerance, not checksum validation. Compatibility behavior around incomplete final CRLF is explicitly accepted by the tests.
