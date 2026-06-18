# File Research: sources/os/linux/linux-stable/fs/proc/self.c

Implements persistent `/proc/self` symlink.

Key points:
- `proc_self_get_link()` returns current task TGID in the proc superblock PID namespace.
- Returns `-ENOENT` if current task is not visible in that namespace.
- Allocates link target with GFP mode depending on RCU/dentry context.
- `proc_setup_self()` creates a persistent symlink dentry during superblock fill.
- `proc_self_init()` allocates stable inode number.

Dependencies/contracts:
- Per-mount PID namespace aware.
- Used by proc root setup.
