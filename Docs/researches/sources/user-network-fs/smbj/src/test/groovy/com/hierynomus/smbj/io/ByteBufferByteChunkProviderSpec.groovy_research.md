# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/ByteBufferByteChunkProviderSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/ByteBufferByteChunkProviderSpec.groovy

Purpose: tests `ByteBufferByteChunkProvider` writing chunks to an output stream. It uses random byte buffers, duplicate buffers for expected comparison, and verifies one full chunk, partial chunk writes, and availability after consuming the first chunk from a buffer larger than `ByteChunkProvider.CHUNK_SIZE`.

State and persistence: in-memory `ByteBuffer` position/remaining state only. Dependencies are Java NIO buffers and SMBJ byte chunk provider APIs. Integration point is file upload/write request chunking from `ByteBuffer`. Risks covered include position mutation, chunk-size boundaries, and correct remaining-byte reporting. Test signal is good for normal buffer-backed streaming.
