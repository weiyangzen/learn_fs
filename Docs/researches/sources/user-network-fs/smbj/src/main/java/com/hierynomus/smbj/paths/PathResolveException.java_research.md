<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/PathResolveException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/PathResolveException.java

Purpose: Checked exception used by path resolvers to return an NT status and optional message/cause when symlink or DFS resolution cannot produce a target path.

Important APIs/types/functions: Constructors accept a raw status, status plus message, or a Throwable. getStatusCode() returns the stored long; getStatus() maps it through NtStatus.valueOf().

Control flow: Resolvers throw this when response error data is missing or referral processing fails. DiskShare catches it and converts it into SMBApiException for SMB2_CREATE. Session.connectTree catches and ignores it for TREE_CONNECT fallback.

State and persistence behavior: Immutable status field only; no persistent state.

Dependencies and integration points: Depends on NtStatus and is consumed by PathResolver, SymlinkPathResolver, DFSPathResolver, DiskShare, and Session.

Risks: The Throwable constructor collapses all causes to STATUS_OTHER, which can hide protocol-specific failure semantics. getStatus() assumes NtStatus.valueOf can represent the stored value.

Test signals: Construct each form and verify status preservation, message/cause propagation, and DiskShare conversion to SMBApiException status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/PathResolveException.java -->
