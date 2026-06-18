<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/File.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/File.java

Purpose: Represents an open regular file and exposes read, write, stream, remote server-side copy, length, truncate, and file-id operations.

Important APIs/types/functions: write() overloads delegate to SMB2Writer. writeAsync() returns aggregate Future<Long>. getOutputStream() supports append by reading FileStandardInformation. read() overloads fill byte arrays or ByteBuffers and map STATUS_END_OF_FILE to -1. read(OutputStream) streams through FileInputStream. remoteCopyTo() and remoteCopyTo(offset, destination, destinationOffset, length) implement FSCTL_SRV_COPYCHUNK. getLength(), setLength(), getInputStream().

Control flow: Reads send SMB2 READ through Share; writes use ByteChunkProvider chunks through SMB2Writer. Remote copy obtains a resume key, sends copy chunk requests, adapts chunk limits if STATUS_INVALID_PARAMETER returns server maxima, and advances offsets by TotalBytesWritten.

State and persistence behavior: Holds SMB2Writer tied to fileId/share/name. Operations mutate remote file data and metadata.

Dependencies and integration points: Extends DiskEntry, depends on Share.read/write/ioctl, CopyChunkRequest/Response, FileStandardInformation, FileEndOfFileInformation, ByteChunkProvider implementations, ProgressListener, and FileInputStream/FileOutputStream.

Risks: remoteCopyTo requires object-identity same share, not equivalent share path. The copy loop can stall if a server returns success with zero TotalBytesWritten. Async writes detect short writes but synchronous writes just accumulates response bytes. Append fetches end-of-file once, so concurrent appenders can race.

Test signals: Byte array and ByteBuffer EOF behavior, stream read/write with progress, async short-write corruption detection, append offset, remote copy limit renegotiation, same-share enforcement, get/set length, and large transfer chunking.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/File.java -->
