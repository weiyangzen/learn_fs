# File Research: sources/os/linux/linux/fs/autofs/autofs_i.h

## Summary
Internal autofs header defining shared state, flags, helpers, and cross-file declarations for the autofs filesystem.

## Main Contents
- `struct autofs_info`: per-dentry/inode state, active/expiring list nodes, requester uid/gid, expiry state, and counters.
- `struct autofs_wait_queue`: daemon wait token, path identity, requester credentials/pids, status, and wait counter.
- `struct autofs_sb_info`: per-superblock control pipe, daemon process group, protocol version, mount type, flags, wait queues, and active/expiring lists.
- Helpers for oz-mode detection, pipe validation/preparation, managed dentry flags, device/inode ids, and expiring-list management.
- Declarations for init, inode, root, symlink, waitq, expire, and misc-device ioctl code.

## Important Behavior
`autofs_oz_mode()` identifies the automount daemon process group or catatonic state. In oz mode the daemon can see/manipulate the raw autofs filesystem without triggering automount behavior.

Managed dentry helpers toggle `DCACHE_NEED_AUTOMOUNT` and `DCACHE_MANAGE_TRANSIT`, which tie autofs dentries into VFS path walking.

Pipe helpers require a writable FIFO, force packet mode through `O_DIRECT`, and clear `O_NONBLOCK`.

## Risks
Most autofs correctness depends on the flags in this header: `PENDING`, `WANT_EXPIRE`, `EXPIRING`, and per-dentry expire timeout state. The active and expiring lists are protected by `lookup_lock`; filesystem state flags use `fs_lock`; wait queues use `wq_mutex`.
