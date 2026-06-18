# sources/user-network-fs/samba/source3/torture/cmd_vfs.c

## Purpose
`cmd_vfs.c` provides the command table for the `vfstest` interactive shell. It lets a developer load VFS modules and call Samba's VFS entry points directly against a test `connection_struct`, making it a manual probe for filesystem modules, ACL paths, named streams, xattrs, directory iteration, and create/open behavior.

## Important APIs, types, and functions
The file exports `vfs_commands[]`, a `struct cmd_set` table consumed by `vfstest.c`. Command handlers all take `struct vfs_state *vfs`, `TALLOC_CTX *mem_ctx`, `argc`, and `argv`, then return `NTSTATUS`. Important handlers include `cmd_load_module`, `cmd_connect`, `cmd_open`, `cmd_close`, `cmd_read`, `cmd_write`, `cmd_stat`/`cmd_fstat`/`cmd_lstat`, xattr handlers, NT ACL handlers, POSIX ACL handlers, `cmd_translate_name`, and `cmd_create_file`. It uses Samba abstractions such as `files_struct`, `smb_filename`, `vfs_open_how`, `synthetic_smb_fname*`, `synthetic_pathref`, `metadata_fsp`, and many `SMB_VFS_*` dispatch macros.

## Control flow
The shell dispatches a parsed command to the matching `cmd_*` function. Path-oriented commands synthesize `smb_filename` objects relative to `vfs->conn->cwd_fsp`, then call the matching VFS hook. Open creates a minimal `files_struct`, resolves stream base objects when needed, opens with `SMB_VFS_OPENAT`, stats the handle, initializes flags and identity fields, and stores the handle in `vfs->files[fd]`. ACL and xattr commands generally open a path reference first, then call fsp-based VFS methods. The shared buffer commands (`populate`, `read`, `write`, `showdata`) feed simple data through later file operations.

## State and persistence behavior
Runtime state lives in `vfs_state`: loaded module chain, open directory handle, `files[]` table, and the shared data buffer. Persistent effects are whatever the invoked VFS module does to the backing share: file creation, deletion, rename, xattr changes, ACL changes, timestamps, symlinks, hard links, and truncation. The code does not maintain durable metadata of its own.

## Dependencies and integration points
This file is built into the `vfstest` binary with `vfstest.c` and `vfstest_chain.c`. It integrates with smbd VFS internals, Samba filename conversion, ACL/security descriptor helpers, passdb machine SID lookup for SDDL encoding, and directory helpers from `source3/smbd/dir.h`.

## Risks and test signals
Many commands trust numeric argv indexes and only some validate `fd < 1024`; bad manual input can dereference missing `vfs->files[fd]`. The command intentionally bypasses full SMB request semantics, so it is best as a VFS hook signal, not as a complete client-behavior test. It is valuable for reproducing VFS module crashes, especially ACL, xattr, pathref, stream, translate-name, and `SMB_VFS_CREATE_FILE` edge cases.
