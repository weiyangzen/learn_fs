# File Research: sources/teaching/xv6-riscv/kernel/sysproc.c

Implements process-related syscalls.

Important behavior:
- Wraps process lifecycle syscalls: `exit`, `fork`, `wait`, `kill`, `getpid`.
- `sys_sbrk()` supports eager and lazy allocation modes using `SBRK_EAGER`/`SBRK_LAZY`.
- `sys_pause()` sleeps for timer ticks and aborts if killed.
- `sys_uptime()` returns tick count under lock.

Filesystem relevance: process lifecycle closes files and drops cwd in `kexit()`. `fork()` duplicates file descriptors and cwd. Lazy allocation affects user buffers used by filesystem syscalls through `copyin`/`copyout`.
