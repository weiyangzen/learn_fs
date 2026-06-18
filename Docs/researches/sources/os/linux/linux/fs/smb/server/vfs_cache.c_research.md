# File Research: sources/os/linux/linux/fs/smb/server/vfs_cache.c

Implements ksmbd open-file caching, inode state tracking, file ID allocation, durable-handle preservation/reconnect, and close teardown.

Key behaviors:
- Maintains a global inode hash keyed by dentry/superblock and protected by `inode_hash_lock`.
- Tracks per-inode open file list, oplock list, delete-pending/delete-on-close flags, and attributes in `struct ksmbd_inode`.
- Maintains global durable file table and per-session volatile file tables with IDR-backed IDs.
- Enforces configurable fd limit through an atomic counter.
- Publishes open files through volatile IDs and optional durable persistent IDs.
- Provides fast/slow/foreign/global/durable lookups with refcount acquisition and tree/persistent ID sanity checks.
- Handles delete-on-close for normal files and stream xattrs; final inode close unlinks pending-delete files.
- Cleans oplocks, byte-range locks, connection references, stream names, durable owner names, and file references during final close.
- Provides tree-connection and session-wide fd close loops with careful locking/refcount handling for in-flight opens and durable preservation.
- Preserves reconnectable durable/resilient/persistent handles across session teardown by detaching `conn`/`tcon`, clearing volatile IDs, storing durable owner identity, removing connection lock/oplock associations, and setting scavenger timeout.
- Runs a durable handle scavenger kthread that expires preserved handles after timeout and safely disposes them.
- Validates durable reconnect path name and reopens durable fds into a new session/connection with lock/oplock reattachment.
- Provides procfs file listing of open handles, access masks, refcounts, and oplock/lease state when procfs is enabled.
- Initializes/destroys file tables, global file table, inode hash, and file slab cache.

Dependencies:
- Uses oplock management, VFS unlink/xattr helpers, connection refs, session/tree/user config, IDR, rwlocks, rwsems, wait queues, freezer-aware kthreads, and procfs helpers.

Role in subsystem:
- Lifetime and identity core for ksmbd open files. It prevents stale handle use, supports SMB durable handles, and coordinates delete-on-close and oplock cleanup.
