# File Research: sources/os/linux/linux/fs/ocfs2/dlmglue.h

Public interface for OCFS2 DLM glue.

Defines LVB formats:
- `struct ocfs2_meta_lvb`, version 5: inode size, clusters, ownership, packed timestamps, mode, link count, attributes, dynamic features, and generation.
- `struct ocfs2_qinfo_lvb`, version 1: quota grace periods, sync interval, block count, free block, and free-entry accounting.
- `struct ocfs2_orphan_scan_lvb`, version 1: orphan-scan sequence number.
- `struct ocfs2_trim_fs_lvb`, version 1: trim success, node number, start, length, minimum length, and trimmed byte count.
- `struct ocfs2_trim_fs_info`: in-memory trim result wrapper.

Defines lock helper state:
- `struct ocfs2_lock_holder` tracks task-owned recursive inode lock context.
- Metadata lock flags: recovery/noqueue/nonblock/get-bh.
- Lockdep subclasses for normal, parent, rename, and reflink target inode locks.

Exports:
- DLM mount lifecycle: `ocfs2_dlm_init()`, `ocfs2_dlm_shutdown()`, `ocfs2_set_locking_protocol()`.
- Lock resource initialization/freeing for inode, dentry, file/flock, quota info, and refcount locks.
- Public lock/unlock helpers for rw, open, inode metadata, super, orphan scan, rename, NFS sync, trim, dentry, flock, quota info, and refcount locks.
- Inode lock convenience macros over `ocfs2_inode_lock_full_nested()`.
- Lock-resource teardown helpers and downconvert-thread wakeup.
- DLM debug reference helpers.
- Recursive-lock tracker pair.

Usage expectations:
- Callers must pair lock/unlock at the matching semantic level, not just matching DLM numeric level.
- `ocfs2_inode_lock()` usually means metadata lock; `ocfs2_rw_lock()` is separate data/rw coordination.
- Nonblocking and GETBH variants are specialized and used to avoid page-lock/DLM inversions or to refresh buffers under already-held locks.
