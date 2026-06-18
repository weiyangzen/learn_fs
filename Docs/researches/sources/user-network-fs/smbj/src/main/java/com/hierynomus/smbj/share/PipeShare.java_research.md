<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/PipeShare.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/PipeShare.java

Purpose: Share subtype for IPC$ named-pipe operations, including waiting for pipe instances and opening NamedPipe handles.

Important APIs/types/functions: waitForPipe(String), waitForPipe(String, long, TimeUnit), open(), openFileId(), and public closeFileId().

Control flow: waitForPipe encodes FsCtlPipeWaitRequest, sends FSCTL_PIPE_WAIT through ioctlAsync, waits slightly longer than requested timeout so the server can return STATUS_IO_TIMEOUT, then returns true for success, false for timeout, or throws SMBApiException. open builds a path under the pipe share and uses Share.openFileId, returning NamedPipe.

State and persistence behavior: No additional state beyond Share; operations interact with remote pipe namespace.

Dependencies and integration points: Extends Share, uses SMBBuffer, FsCtlPipeWaitRequest, ArrayByteChunkProvider, SMB2 IOCTL response status, and NamedPipe.

Risks: timeoutMs adds only 20 ms margin and can be flaky under latency. Indefinite waits use receive with timeout zero. Name must exclude `\pipe\` but method does not validate it.

Test signals: Available pipe, timeout pipe, error status, indefinite wait, name encoding, open with access masks/options, and closeFileId exposure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/PipeShare.java -->
