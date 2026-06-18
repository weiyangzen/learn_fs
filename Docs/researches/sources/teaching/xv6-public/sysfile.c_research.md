# File Research: sources/teaching/xv6-public/sysfile.c

Implements file-system-related system calls.

Key behavior:
- `argfd` validates fd arguments and resolves `struct file`.
- `fdalloc` installs a file in the first free per-process fd slot.
- Implements `dup`, `read`, `write`, `close`, and `fstat`.
- `sys_link` increments link count, links new directory entry, and rolls back on failure.
- `sys_unlink` removes directory entries, prevents unlinking `.`/`..`, checks directory emptiness, and decrements link counts.
- `create` allocates files, directories, or device inodes and installs `.`/`..` for directories.
- `sys_open` handles create and open modes, forbids write-opening directories, allocates file/fd state, and sets readability/writability.
- Implements `mkdir`, `mknod`, `chdir`, `exec`, and `pipe`.

Important interactions:
- Mutating filesystem syscalls use `begin_op`/`end_op`.
- Directory link counts are maintained for `..`.
- `sys_pipe` must unwind partially allocated fd/file state on failure.
