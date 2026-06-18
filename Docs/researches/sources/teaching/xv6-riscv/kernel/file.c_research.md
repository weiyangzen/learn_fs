# File Research: sources/teaching/xv6-riscv/kernel/file.c

Implements the global open-file table and high-level file operations over pipes, devices, and inodes.

Important behavior:
- `fileinit()` initializes the table lock.
- `filealloc()` finds a free `struct file` and sets `ref = 1`.
- `filedup()` increments file references.
- `fileclose()` decrements references and closes pipes or drops inode references in a transaction.
- `filestat()` locks an inode and copies `struct stat` to user memory.
- `fileread()` dispatches to pipe, device, or inode read and advances inode offsets.
- `filewrite()` dispatches to pipe/device/inode writes and chunks inode writes to fit log transaction capacity.

Filesystem relevance: this is the VFS-like dispatch layer of xv6. It bridges syscall file descriptors to inode operations, pipe operations, and device switch handlers.
