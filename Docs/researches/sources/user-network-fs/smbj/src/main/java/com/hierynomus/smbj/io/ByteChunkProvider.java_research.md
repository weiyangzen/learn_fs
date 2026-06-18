# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/ByteChunkProvider.java

Purpose: `ByteChunkProvider` is the abstract base for streaming data into SMB write requests.

Important APIs and control flow: subclasses report availability, prepare data, provide chunks, and report bytes left. Base methods write one or more chunks to an `OutputStream` or protocol `Buffer`, update remote offset by written size, and track `lastWriteSize`. IO failures are wrapped as `SMBRuntimeException`.

State, dependencies, and integration: shared state includes remote `offset`, `chunkSize` defaulting to 64 KiB, and `lastWriteSize`. Used by share/file write implementations.

Risks: allocates a fresh chunk buffer per write call. Runtime wrapping hides checked IO from callers. Tests should cover offset and last-write updates, multi-chunk writes, zero-byte providers, and close behavior.
