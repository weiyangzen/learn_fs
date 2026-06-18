# File Research: sources/teaching/minix/minix/servers/vfs/table.c

## Purpose
Defines the VFS syscall dispatch table `call_vec`, mapping `VFS_*` call numbers to their implementing `do_*` routines.

## Main Data
- `CALL(n)` converts absolute VFS call numbers into zero-based indices relative to `VFS_BASE`.
- `call_vec[NR_VFS_CALLS]` is a designated-initializer array of function pointers.

## Coverage
The table includes core file operations (`read`, `write`, `open`, `close`), namespace calls (`link`, `unlink`, `rename`, `mkdir`, `rmdir`), metadata calls (`stat`, `fstat`, `lstat`, `chmod`, `chown`, `utimens`), mount/statvfs calls, VM/VFS coordination, driver mapping, and socket operations.

## Dependencies
Includes `fs.h`, MINIX call number headers, and VFS object headers so the function declarations and syscall constants are visible.

## Risks and Notes
This table is central dispatch glue: missing or mismatched call numbers would route syscalls incorrectly. `VFS_RMDIR` deliberately maps to `do_unlink`, implying the unlink implementation distinguishes file and directory removal by call/message context.
