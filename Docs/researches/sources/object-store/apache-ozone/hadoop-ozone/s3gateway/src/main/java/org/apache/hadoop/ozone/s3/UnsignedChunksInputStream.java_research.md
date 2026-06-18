# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/UnsignedChunksInputStream.java

Purpose: `UnsignedChunksInputStream` unwraps AWS streaming unsigned chunked payloads, including trailer-style bodies, and exposes only object payload bytes.

Important APIs and flow: it mirrors `SignedChunksInputStream` without a `chunk-signature` parser. `readContentLengthFromHeader` reads a CRLF-terminated hex length line; zero marks the final chunk and later trailer bytes are ignored. Both single-byte and buffer reads consume trailing CRLF after each payload chunk.

State, dependencies, risks, and tests: state is `remainingData` and final-chunk flag. It integrates with `EndpointBase.getS3ChunkInputStreamInfo` for `STREAMING-UNSIGNED-PAYLOAD-TRAILER`. The explicit risk is that trailer checksum verification is not implemented, so bad trailer checksums are ignored. Additional risks include malformed hex lines, integer overflow, premature EOF, and CRLF assumptions. Tests should cover trailers, multi-buffer chunk boundaries, empty chunks, invalid lengths, and consistency between read overloads.
