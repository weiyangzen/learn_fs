<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/FileInputStream.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/FileInputStream.java

Purpose: InputStream adapter for reading an SMB file with asynchronous read-ahead.

Important APIs/types/functions: read(), read(byte[], int, int), close(), available(), skip(), loadBuffer(), sendRequest().

Control flow: On first read it sends or awaits nextResponse. A successful read stores response data in buf, advances offset by data length, notifies ProgressListener, and immediately sends the next async read for read-ahead. STATUS_END_OF_FILE or zero-length data marks the stream closed and subsequent reads return -1.

State and persistence behavior: Maintains remote file handle reference, logical offset, current buffer index, current buffer, progress listener, isClosed, and nextResponse. No persistence.

Dependencies and integration points: Uses File.readAsync(), Futures.get(timeout), SMB2ReadResponse, NtStatus, ProgressListener, and TransportException wrapping.

Risks: close() does not cancel an outstanding nextResponse. available() always returns zero. skip() can advance beyond EOF and does not validate negative n. Not thread-safe. If read(byte[], off, len) is called with len zero on a closed stream it returns -1 rather than Java InputStream's usual zero.

Test signals: Single-byte and bulk reads, EOF from status and zero-length data, progress offsets, read-ahead issuance, timeout conversion, skip within buffer and beyond buffer, close-before-response, and zero-length read semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/FileInputStream.java -->
