# File Research: sources/os/linux/linux-stable/fs/smb/server/vfs.c

## Summary
Implements ksmbd’s VFS abstraction layer: path lookup inside shares, file and directory create/remove/rename/link, read/write/fsync/truncate, named-stream xattr I/O, extended attributes, sparse/allocated-range operations, copychunk, directory helpers, Windows metadata xattr storage, security descriptor xattr storage, and POSIX ACL initialization/inheritance.

## Main Responsibilities
- Resolve share-relative paths with `LOOKUP_BENEATH`, optional case-insensitive directory walking, optional cross-mount following, and removal/create-specific locking.
- Create files and directories, optionally inheriting owner from parent.
- Enforce SMB desired-access rights and byte-range lock conflicts before reads, writes, truncates, and copychunk.
- Read/write normal files through `kernel_read()`/`kernel_write()` and named streams through `user.DosStream.*` xattrs.
- Break level-II oplocks before writes, truncates, zeroing, and copy-range writes.
- Remove files/directories, hardlink, rename, unlink by open file, and test directory emptiness.
- List, get, set, remove, and case-insensitively find xattrs.
- Convert SMB caching options into Linux file flags/readahead behavior.
- Implement zero-data and allocated-range queries with fallocate/lseek.
- Store and retrieve DOS attribute xattrs via NDR encoding.
- Store and retrieve NT security descriptor xattrs with NDR encoding and SHA-256 hashes of the descriptor and current POSIX ACL state.
- Fill SMB directory/stat metadata from `kstat`, DOS attributes, and timestamps.
- Initialize POSIX ACLs from mode and inherit POSIX ACLs from parent default ACLs.

## Key Interfaces
Major exported helpers include `ksmbd_vfs_create()`, `ksmbd_vfs_mkdir()`, `ksmbd_vfs_read()`, `ksmbd_vfs_write()`, `ksmbd_vfs_fsync()`, `ksmbd_vfs_remove_file()`, `ksmbd_vfs_link()`, `ksmbd_vfs_rename()`, `ksmbd_vfs_truncate()`, `ksmbd_vfs_copy_file_ranges()`, `ksmbd_vfs_kern_path()`, `ksmbd_vfs_kern_path_start_removing()`, `ksmbd_vfs_kern_path_create()`, `ksmbd_vfs_set_sd_xattr()`, `ksmbd_vfs_get_sd_xattr()`, `ksmbd_vfs_set_dos_attrib_xattr()`, and `ksmbd_vfs_fill_dentry_attrs()`.

## Important Behavior
Path lookup keeps clients inside the share with `LOOKUP_BENEATH` for non-root paths. Case-insensitive lookup retries by iterating each path component directory and replacing the requested component with the actual on-disk spelling.

Named streams are represented as xattrs whose names are built from `user.DosStream.<stream>:$DATA` or `:$INDEX_ALLOCATION`. Stream writes are capped at `XATTR_SIZE_MAX` and rewrite the whole xattr value.

NTACL xattr storage uses Samba-compatible NDR v4 structures. Before storing, security descriptor offsets are shifted by `NDR_NTSD_OFFSETOF`; on load they are shifted back. A hash of current POSIX ACL state is checked before accepting the stored NT security descriptor.

Copychunk verifies source and destination access, rejects named streams, checks byte-range locks, avoids overlapping same-inode copy with direct `vfs_copy_file_range()`, and falls back to splice-based copying when needed.

## Cross-File Interactions
Uses access/credential helpers from `smb_common.c`, open state from `vfs_cache.c`, oplock breaking from `oplock.c`, ACL conversion from `smbacl.c`, NDR helpers, xattr formats from `xattr.h`, share config flags, and stats counters.

## Risks
This is a high-risk file because it bridges SMB semantics to Linux VFS semantics. Path traversal containment, write-mount acquisition/drop, xattr size handling, NTACL hash validation, stream xattr rewriting, lock conflict checks, idmapped ownership, and close/delete interactions must stay correct under concurrent client activity.
