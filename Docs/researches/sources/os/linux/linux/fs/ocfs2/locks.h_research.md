# File Research: sources/os/linux/linux/fs/ocfs2/locks.h

`locks.h` declares OCFS2’s userspace file locking hooks:
- `ocfs2_flock()` for BSD flock operations.
- `ocfs2_lock()` for POSIX byte-range locks.

It is a small prototype header used by file operation setup code.
