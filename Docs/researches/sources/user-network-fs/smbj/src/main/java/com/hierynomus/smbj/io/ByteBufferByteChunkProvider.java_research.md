# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/ByteBufferByteChunkProvider.java

Purpose: `ByteBufferByteChunkProvider` adapts a Java `ByteBuffer` to cached SMB write chunks.

Important APIs and control flow: `prepareChunk` reads up to destination length, requested bytes, and `buffer.remaining()`, returning -1 when no bytes are needed. `isAvailable` checks both cached data and remaining source buffer bytes.

State, dependencies, and integration: extends `CachingByteChunkProvider`; constructors optionally set remote file offset.

Risks: advances the caller-supplied `ByteBuffer` position. Tests should cover prepare/write cycles, zero-byte prepare, direct and heap buffers, offset propagation, and availability before and after cache fill.
