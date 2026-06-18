# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/InputStreamByteChunkProvider.java

Purpose: `InputStreamByteChunkProvider` adapts an `InputStream` to the cached chunk provider contract.

Important APIs and control flow: constructor uses an existing `BufferedInputStream` as-is or wraps the stream and marks it owned. `prepareChunk` reads up to requested bytes and chunk length. `isAvailable` returns cached availability or `is.available() > 0`. `close` closes only streams it wrapped itself.

State, dependencies, and integration: extends `CachingByteChunkProvider`; used directly and by `FileByteChunkProvider`.

Risks: `InputStream.available()` is not a reliable EOF or readiness signal for all streams. A provided `BufferedInputStream` is not closed by this provider. Tests should cover wrapped versus unwrapped close ownership, EOF reads, partial availability, and IO exception wrapping.
