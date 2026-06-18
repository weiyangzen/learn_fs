
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestSignedChunksInputStream.java

Purpose: tests decoding of AWS signed chunked upload bodies by `SignedChunksInputStream`.

Important APIs and control flow: covers empty body, empty body with trailer, empty body without final CRLF, single chunk, single chunk with trailer, single chunk without final terminator, multiple chunks, and multiple chunks with trailer. Each scenario wraps encoded bytes and asserts decoded content through full `IOUtils.toString`, full byte-array reads, and partial reads.

State, dependencies, integration: no persistent state; uses `ByteArrayInputStream` and UTF-8 assertions. Integrated with S3 streaming upload handling and `x-amz-content-sha256` streaming signatures.

Risks and test signals: tests verify chunk framing removal but not cryptographic signature validation. It includes trailer formats and missing-end tolerance, which are important compatibility signals.
