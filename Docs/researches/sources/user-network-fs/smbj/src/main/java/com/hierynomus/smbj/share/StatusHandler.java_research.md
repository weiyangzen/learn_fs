<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/StatusHandler.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/StatusHandler.java

Purpose: Small status-policy interface used to decide whether an SMB2 response status is acceptable for a particular operation.

Important APIs/types/functions: SUCCESS singleton returns true only for NtStatus.STATUS_SUCCESS. Implementations provide isSuccess(long).

Control flow: Share.receive checks a response header status with a supplied StatusHandler and throws SMBApiException if false. PathResolver decorators expose handlers that accept resolution-triggering statuses.

State and persistence behavior: Stateless strategy objects.

Dependencies and integration points: Uses NtStatus. Implemented anonymously in Share, DiskShare, DFSPathResolver, SymlinkPathResolver, and PipeShare handling.

Risks: Incorrect handlers can cause either premature exceptions or accidental acceptance of real errors. Because it sees only status code, it cannot inspect response-specific error payloads.

Test signals: SUCCESS policy, composed DFS/symlink policies, and per-operation handlers rejecting unexpected statuses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/StatusHandler.java -->
