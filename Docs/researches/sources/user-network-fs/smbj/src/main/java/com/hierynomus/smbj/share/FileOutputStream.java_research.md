<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/FileOutputStream.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/FileOutputStream.java

Purpose: OutputStream adapter that buffers bytes into a RingBuffer and writes them to an SMB file through SMB2Writer.

Important APIs/types/functions: write(int), write(byte[], int, int), flush(), close(), verifyConnectionNotClosed(), and ByteArrayProvider extending ByteChunkProvider.

Control flow: Writes fill the provider's ring buffer. If the buffer is full or would overflow, flush sends the current provider through SMB2Writer.write(), which consumes chunks and advances provider offset. close drains all available bytes, resets the provider buffer, marks closed, and drops writer reference.

State and persistence behavior: Holds SMB2Writer, ProgressListener, closed flag, and ByteArrayProvider with RingBuffer and current offset. Mutates remote file data when flushed/closed.

Dependencies and integration points: Used by SMB2Writer.getOutputStream() and File.getOutputStream(). Relies on RingBuffer and ByteChunkProvider offset management.

Risks: close() calls provider.reset() before logging provider.getOffset(), but provider still exists while buf is null; getOffset comes from ByteChunkProvider and should be safe. close() does not call flush() through the public method after closed. Not thread-safe. Large writes split by provider.maxSize() and depend on RingBuffer correctness.

Test signals: Buffer boundary writes, close drains remaining bytes, write after close IOException, progress callbacks, append offset propagation, and exact offset advancement after multiple flushes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/FileOutputStream.java -->
