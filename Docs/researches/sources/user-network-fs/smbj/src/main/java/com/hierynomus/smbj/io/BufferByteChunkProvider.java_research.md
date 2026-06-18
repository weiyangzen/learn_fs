# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/BufferByteChunkProvider.java

Purpose: `BufferByteChunkProvider` streams chunks from SMBJ's protocol `Buffer`.

Important APIs and control flow: `isAvailable` and `bytesLeft` mirror `buffer.available()`. `getChunk` reads the smaller of destination length and available bytes, wrapping `BufferException` as `IOException`.

State, dependencies, and integration: used directly for buffer-backed writes and internally by `CachingByteChunkProvider`.

Risks: consumes from the buffer's read position. Tests should cover exact, short, and exhausted reads plus exception wrapping.
