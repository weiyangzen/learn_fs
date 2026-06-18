<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/NamedPipe.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/NamedPipe.java

Purpose: Represents an open SMB named pipe and exposes pipe read/write, transceive, peek, and IOCTL helpers.

Important APIs/types/functions: write(byte[]), write(byte[], int, int), read(byte[]), read(byte[], int, int), transact(), peek(), ioctl overloads, and getName().

Control flow: Writes wrap input in ArrayByteChunkProvider and call Share.write at offset zero. Reads call Share.read at offset zero and copy response data into caller buffer. transact uses FSCTL_PIPE_TRANSCEIVE. peek uses FSCTL_PIPE_PEEK and decodes FsCtlPipePeekResponse from SMBBuffer.

State and persistence behavior: Inherits fileId/name/share from Open; pipe operations affect server pipe state but no local persistent state.

Dependencies and integration points: Used by PipeShare.open(). Depends on fsctl pipe structures, Share read/write/ioctl, SMBBuffer, and SMBRuntimeException.

Risks: read ignores STATUS_END_OF_FILE special semantics and returns zero if server returns no data. transact(byte[]) allocates output from IOCTL response size, while fixed-buffer overload truncates to caller length. No stream facade or async pipe APIs here.

Test signals: Pipe open/read/write, partial buffer offsets, FSCTL_PIPE_TRANSCEIVE with variable/fixed output, peek maxDataSize parsing, and IOCTL error propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/NamedPipe.java -->
