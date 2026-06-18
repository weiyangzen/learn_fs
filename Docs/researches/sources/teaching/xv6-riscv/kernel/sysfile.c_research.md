# File Research: sources/teaching/xv6-riscv/kernel/sysfile.c

Implements filesystem and file-descriptor syscalls.

Important behavior:
- `argfd()` validates a user file descriptor and returns `struct file`.
- `fdalloc()` installs a file reference into the current process table.
- Implements `dup`, `read`, `write`, `close`, and `fstat`.
- `sys_link()` increments inode link count, links into new parent directory, and rolls back on failure.
- `sys_unlink()` removes directory entries, handles directory emptiness, decrements links, and triggers inode cleanup through `iput()`.
- `create()` handles file/device/directory inode creation plus `.` and `..`.
- `sys_open()` handles create, directory write restrictions, device validation, file allocation, flags, and truncation.
- `sys_mkdir()`, `sys_mknod()`, `sys_chdir()`, `sys_exec()`, and `sys_pipe()` bridge user arguments to lower layers.

Filesystem relevance: this is the user-facing filesystem syscall layer. It enforces basic Unix semantics and transaction boundaries while delegating storage mechanics to `file.c` and `fs.c`.
