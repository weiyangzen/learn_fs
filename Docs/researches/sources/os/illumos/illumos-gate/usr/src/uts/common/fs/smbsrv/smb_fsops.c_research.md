# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_fsops.c

## Role

CIFS-aware filesystem operation layer. It sits above `smb_vop_*` and below SMB command handlers, adding SMB semantics for access checks, share boundaries, streams, short-name mangling, ACL/security descriptor handling, byte-range/share locks, notifications, and read/write behavior.

## Major Responsibilities

- Converts SMB access masks to VOP open modes.
- Wraps VFS open/close/create/mkdir/remove/rmdir/link/rename/getattr/setattr/read/write/statfs/commit operations.
- Enforces tree containment, share access masks, readonly shares, ACE permissions, and open-file granted access.
- Handles named streams using extended-attribute vnode operations and unnamed-stream authorization.
- Blocks restricted stream names for non-kernel credentials.
- Handles mangled 8.3 names and exact case-sensitive follow-up operations.
- Applies Windows security descriptor inheritance for ZFS/ACE ACL targets.
- Reads, writes, merges, and inherits owner/group/DACL/SACL security data.
- Issues file-change notifications after namespace, stream, ACL, and create/remove operations.
- Checks SMB byte-range lock conflicts before read/write.
- Preserves pending mtime semantics after writes through handles with manually set mtime.
- Provides zero-copy buffer request/return wrappers and sparse-range helpers.
- Implements share reservations and byte-range lock VOP translations.

## Key Functions

- `smb_fsop_amask_to_omode()` maps SMB desired access to `FREAD`, `FWRITE`, and `FAPPEND`.
- `smb_fsop_create()` handles regular file and stream creates, including share containment, readonly checks, CATIA/ABE/case flags, and mangled-name collision checks.
- `smb_fsop_create_file_with_stream()` creates a base file if needed, then creates a named stream, removing the base file on stream-create failure.
- `smb_fsop_create_stream()` creates a named stream and aligns UID/GID with the unnamed stream.
- `smb_fsop_create_file()` creates regular files, applying incoming or inherited security descriptors when available.
- `smb_fsop_mkdir()` creates directories with analogous ACL inheritance/security descriptor behavior.
- `smb_fsop_remove()` removes files or streams, including stream parsing, restricted stream checks, mangled-name fallback, and notifications.
- `smb_fsop_remove_streams()` enumerates and removes all streams from a file.
- `smb_fsop_rmdir()` removes directories with mangled-name fallback and notifications.
- `smb_fsop_getattr()` checks tree/open access, handles named-stream unnamed vnode context, and marks DFS links as directories.
- `smb_fsop_link()` creates hard links after tree and readonly checks.
- `smb_fsop_rename()` validates source/destination permissions, rejects mount points and reparse points, checks open-handle delete access, performs rename, updates node cache naming, and emits rename/remove/add notifications.
- `smb_fsop_setattr()` checks write permissions by attribute class and calls `smb_vop_setattr()`.
- `smb_fsop_freesp()` supports valid-data-length zeroing/free-space operations via `VOP_SPACE`.
- `smb_fsop_read()` and `smb_fsop_write()` enforce tree/open access, stream credentials, mandatory lock conflicts, critical regions, and VOP I/O.
- `smb_fsop_next_alloc_range()` uses `_FIO_SEEK_DATA` and `_FIO_SEEK_HOLE`.
- `smb_fsop_statfs()` wraps filesystem statfs.
- `smb_fsop_access()` implements SMB access checks, including readonly denial, reparse delete denial, stream behavior, `ACCESS_SYSTEM_SECURITY`, share mask filtering, and ACE/POSIX access translation.
- `smb_fsop_lookup_name()`, `smb_fsop_lookup_file()`, `smb_fsop_lookup_stream()`, and `smb_fsop_lookup()` implement file/stream lookup, path containment, symlink following, traversal checks, CATIA/ABE/case flags, and short-name unmangling.
- `smb_fsop_aclread()` and `smb_fsop_aclwrite()` translate ACLs between filesystem and SMB expectations.
- `smb_fsop_sdread()`, `smb_fsop_sdmerge()`, `smb_fsop_sdwrite()`, and `smb_fsop_sdinherit()` handle security descriptor read/write/merge/inheritance.
- `smb_fsop_eaccess()` computes effective SMB-style access from filesystem access.
- `smb_fsop_shrlock()` and `smb_fsop_unshrlock()` manage share reservations.
- `smb_fsop_frlock()` maps SMB byte-range locks to `flock64_t` remote locks while skipping zero-length and wraparound ranges.

## Research Notes

This is the main semantic boundary between SMB protocol rules and illumos VFS. Command handlers should call `smb_fsop_*` rather than raw `smb_vop_*` so tree policy, stream rules, Windows ACL behavior, notifications, and open-handle semantics remain consistent.
