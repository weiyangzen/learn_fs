# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/CachingByteChunkProvider.java

Purpose: `CachingByteChunkProvider` buffers source data before write calls so stream-like sources can be prepared to a target size.

Important APIs and control flow: constructor creates a big-endian plain buffer and a `BufferByteChunkProvider` over it. `prepareWrite` compacts the cache, computes bytes needed, repeatedly calls subclass `prepareChunk`, and appends data to the cache until enough data or EOF. `getChunk`, `bytesLeft`, `isAvailable`, and `close` delegate to the cache provider.

State, dependencies, and integration: base for `InputStreamByteChunkProvider` and `ByteBufferByteChunkProvider`.

Risks: read buffer is fixed at 1024 bytes, which may limit preparation efficiency. `buffer` is never null despite guard. Tests should cover compaction, EOF handling, partial fills, repeated prepare/write loops, and runtime wrapping of IO failures.
