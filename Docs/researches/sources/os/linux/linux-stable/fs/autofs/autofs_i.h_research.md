# File Research: sources/os/linux/linux-stable/fs/autofs/autofs_i.h

## Purpose
Internal autofs header defining shared structures, flags, prototypes, and inline helpers for the autofs filesystem implementation.

## Main Contents
- `struct autofs_info`: per-dentry/inode state, active/expiring list links, expire state, last-used time, requester uid/gid, and per-dentry timeout.
- `struct autofs_sb_info`: per-superblock daemon pipe, protocol version, flags, mount namespace id, locks, active/expiring lists, and wait queues.
- Wait queue state in `struct autofs_wait_queue`.
- Superblock flags including catatonic, strict-expire, and ignore.
- Dentry managed-flag helpers for `DCACHE_NEED_AUTOMOUNT` and `DCACHE_MANAGE_TRANSIT`.
- Pipe validation/preparation helpers and shared prototypes.

## Important Behavior
`autofs_oz_mode()` identifies daemon/catatonic access, allowing the owner process group to see and mutate the raw autofs namespace without triggering automounts. The header centralizes expiring-list manipulation under `lookup_lock` and wraps pipe setup to require writable FIFO packet-mode pipes.

## Cross-File Relationships
Included by all autofs implementation files. `root.c` uses dentry and automount helpers, `waitq.c` uses wait queue structures, `expire.c` uses expire flags/lists, `inode.c` initializes superblock state, and `dev-ioctl.c` exposes control operations.

## Risks / Review Notes
`autofs_info` is RCU-freed and linked into active/expiring lists; users must respect locking and lifetime. `autofs_empty()` depends on the internal `count` convention used by namespace mutation code.
