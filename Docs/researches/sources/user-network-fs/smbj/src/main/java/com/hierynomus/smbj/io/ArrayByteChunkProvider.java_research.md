# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/ArrayByteChunkProvider.java

Purpose: `ArrayByteChunkProvider` streams chunks from an in-memory byte array.

Important APIs and control flow: constructor captures source array, buffer offset, length, and remote file offset. `getChunk` copies up to the chunk buffer length, advances the array offset, and decrements remaining bytes. `prepareWrite` is a no-op.

State, dependencies, and integration: used by SMB write paths that can source data from byte arrays.

Risks: source array is not copied, so caller mutation affects writes. Constructor does not validate offset/length bounds. Tests should cover partial writes, file offset reporting, bytes-left updates, and invalid constructor ranges.
