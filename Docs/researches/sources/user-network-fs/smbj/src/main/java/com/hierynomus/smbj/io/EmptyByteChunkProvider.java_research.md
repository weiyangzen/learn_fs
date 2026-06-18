# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/EmptyByteChunkProvider.java

Purpose: `EmptyByteChunkProvider` represents an empty write source at a given file offset.

Important APIs and control flow: `isAvailable` is false, `getChunk` and `bytesLeft` return zero, and `prepareWrite` is a no-op.

State, dependencies, and integration: used when a write path needs a provider object but no payload bytes.

Risks: callers must not assume `getChunk` returning zero means progress. Tests should cover offset initialization and no writes emitted.
