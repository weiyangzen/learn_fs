# File Research: sources/teaching/xv6-public/sysproc.c

Implements process/time-related system calls.

Functions:
- `sys_fork`, `sys_exit`, `sys_wait`, `sys_kill`, `sys_getpid`.
- `sys_sbrk` grows/shrinks process memory through `growproc`.
- `sys_sleep` sleeps for a tick count while watching `killed`.
- `sys_uptime` returns global tick count.

Important interactions:
- `sys_sleep` uses `tickslock` and sleeps on `ticks`.
- `sys_exit` never returns, but includes a dummy return for type checking.
