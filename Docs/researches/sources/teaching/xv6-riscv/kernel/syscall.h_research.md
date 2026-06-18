# File Research: sources/teaching/xv6-riscv/kernel/syscall.h

Defines syscall numbers.

Filesystem-related syscall numbers include:
- `SYS_pipe`, `SYS_read`, `SYS_exec`, `SYS_fstat`, `SYS_chdir`, `SYS_dup`, `SYS_open`, `SYS_write`, `SYS_mknod`, `SYS_unlink`, `SYS_link`, `SYS_mkdir`, `SYS_close`.

Filesystem relevance: this is the ABI mapping between user stubs and kernel syscall dispatch.
