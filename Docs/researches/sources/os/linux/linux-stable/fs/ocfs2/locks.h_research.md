# File Research: sources/os/linux/linux-stable/fs/ocfs2/locks.h

Purpose: declares OCFS2 file locking entry points for VFS file operations.

Read coverage: complete file read, 16 lines.

Declared APIs:
- `ocfs2_flock()` handles BSD flock-style locking.
- `ocfs2_lock()` handles POSIX byte-range locking.

Important dependencies:
- Uses Linux `struct file` and `struct file_lock`; implementation is in `locks.c`.

Risk and edge cases:
- The two APIs have different cluster backends in the implementation: flock uses OCFS2 file locks, while POSIX locks use plocks.
