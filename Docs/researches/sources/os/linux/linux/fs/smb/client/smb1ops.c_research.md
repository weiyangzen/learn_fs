# File Research: sources/os/linux/linux/fs/smb/client/smb1ops.c

This file binds SMB1/CIFS-specific behavior into `struct smb_version_operations` and `struct smb_version_values`. It adapts generic CIFS VFS operations to SMB1 wire commands and legacy server capabilities.

Major responsibilities:
- `reset_cifs_unix_caps()` negotiates CIFS Unix Extensions, preserving reconnect semantics, honoring mount options, and enabling POSIX ACL/path flags on the superblock.
- Cancel paths implement `SMB_COM_NT_CANCEL` and lock-cancel fallback for Windows blocking locks.
- MID, credit, read-offset/length, oplock, negotiate, echo, and path-accessibility helpers provide SMB1-specific operation semantics.
- Read/write size negotiation accounts for Unix large read/write caps, `CAP_LARGE_READ_X`, `CAP_LARGE_WRITE_X`, signing limitations, server `maxBuf`, and hard CIFS limits.
- `cifs_query_path_info()` layers multiple metadata fallbacks: `CIFSSMBQPathInfo()`, `CIFSFindFirst()`, and legacy `SMBQueryInformation()`, with special handling for non-Unicode wildcard paths and non-NT servers.
- SMB1 reparse support is integrated by detecting `ATTR_REPARSE_POINT`, fetching WSL `$LXMOD`/`$LXDEV` EAs when xattrs are enabled, calling `cifs_query_reparse_point`, and exposing `cifs_get_reparse_point_buffer()`.
- `cifs_make_node()` chooses Unix Extensions, SFU emulation, or reparse-point creation for special files.
- `smb_set_file_info()` implements robust attribute/time setting with path-based, filehandle-based, and legacy `SMB_COM_SETATTR` fallbacks.

Operations table:
- `smb1_operations` wires SMB1 implementations for negotiate, session setup, tree connect/disconnect, query/set metadata, reparse operations, open/close/flush, sync/async I/O, directory enumeration, locking, ACLs, symlinks, special-node creation, stats, and network-name-deleted detection.
- `smb1_values` defines SMB1 constants such as protocol id, header sizes, lock types, read response size, capability bits, and signing mode bits.

Risk points:
- Many paths exist for old/non-NT/non-Unicode servers, so behavior is highly capability-dependent.
- Metadata fallback code must preserve semantic differences between NT-style “zero means unchanged” times and legacy servers where zero can be a real timestamp.
