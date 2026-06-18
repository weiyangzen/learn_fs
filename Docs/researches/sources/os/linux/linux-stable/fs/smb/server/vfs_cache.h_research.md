# File Research: sources/os/linux/linux-stable/fs/smb/server/vfs_cache.h

## Summary
Defines ksmbd file-handle, inode-cache, lock, stream, durable-owner, and file-table structures plus the public cache/lifetime API.

## Main Responsibilities
- Define Windows-style generic file permission constants and sentinel FID values.
- Define `struct ksmbd_lock` for byte-range lock tracking.
- Define `struct ksmbd_inode` for per-dentry shared open/oplock/delete state.
- Define `struct ksmbd_file` for per-open state, ids, access/share modes, oplock pointer, stream state, readdir state, durable flags, client/create GUIDs, owner identity, and lists.
- Define `struct ksmbd_file_table` wrapping an IDR and lock.
- Provide helpers for dir-context actor setup, FID validity, and stream detection.
- Declare all open/close/lookup, durable handle, inode status, file-table, fd-limit, and file-cache lifecycle functions.

## Cross-File Interactions
Consumed by SMB2 open/close/read/write/lock/durable-handle paths, VFS operations, oplock handling, connection/session cleanup, and proc reporting.

## Risks
The structures encode object ownership and synchronization assumptions. Layout or semantic changes can break handle lookup, durable reconnect, lock cleanup, delete-on-close, or oplock lifetime.
