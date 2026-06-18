# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/SignedChunksInputStream.java

Purpose: `SignedChunksInputStream` unwraps AWS SigV4 streaming signed chunked upload bodies so downstream object-write code reads only object payload bytes.

Important APIs and flow: `read()` and `read(byte[], int, int)` maintain `remainingData` for the current chunk and `isFinalChunkEncountered` for EOF. When a new chunk is needed, `readContentLengthFromHeader` reads until CRLF, matches `([0-9A-Fa-f]+);chunk-signature=.*`, parses the hex chunk length, and returns zero for the final chunk. After each data chunk it consumes the trailing CRLF.

State, dependencies, risks, and tests: state is per-stream chunk parser state; there is no persistence. It integrates with `EndpointBase.getS3ChunkInputStreamInfo` for multi-chunk signed payloads. The class explicitly does not verify chunk signatures or trailers, so security depends on higher-level request authentication and optional digest behavior. Risks include malformed chunk handling, integer length limits, ignored trailer checksum/signature, and recursive single-byte read. Tests should cover multiple chunks, final zero chunk, trailers, invalid signature line, buffer boundaries, and premature EOF.
