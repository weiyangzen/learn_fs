# File Research: sources/teaching/minix/minix/servers/vfs/lock.c

POSIX advisory file locking implementation.

Key functions:
- `lock_op`: handles `F_GETLK`, `F_SETLK`, and `F_SETLKW`.
- `lock_revive`: wakes processes blocked on locks.

`lock_op` behavior:
- Copies `struct flock` from user space.
- Validates lock type, request type, file type, and descriptor access mode.
- Converts `l_whence`, `l_start`, and `l_len` into an absolute byte range.
- Checks for overlapping conflicting locks.
- `F_GETLK` reports the conflicting lock or `F_UNLCK`.
- `F_SETLK` returns `EAGAIN` on conflict.
- `F_SETLKW` saves request state in `fp_flock`, suspends process, and returns `SUSPEND`.
- Unlocking can remove, shrink, or split existing lock entries.
- New locks are stored in `file_lock[]`.

Limitations:
- Fixed table size `NR_LOCKS`.
- A process’s own locks are not treated as conflicts.
- Unlocking the middle of a region requires a spare lock entry.
- `lock_revive` wakes all blocked lock waiters rather than identifying only affected ones.
