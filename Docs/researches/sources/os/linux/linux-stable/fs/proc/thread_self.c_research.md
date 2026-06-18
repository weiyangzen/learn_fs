# File Research: sources/os/linux/linux-stable/fs/proc/thread_self.c

Implements persistent `/proc/thread-self` symlink.

Key points:
- Link target is `<tgid>/task/<pid>` for the current thread in the proc superblock PID namespace.
- Returns `-ENOENT` if current thread is invisible in that namespace.
- Allocates target buffer with GFP mode appropriate for lookup context.
- `proc_setup_thread_self()` creates persistent symlink dentry during superblock fill.
- `proc_thread_self_init()` allocates stable inode number.

Dependencies/contracts:
- Per-mount PID namespace aware.
- Complements `/proc/self` for thread-specific proc access.
