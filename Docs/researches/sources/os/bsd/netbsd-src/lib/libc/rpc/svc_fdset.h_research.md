# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_fdset.h

Read completely: 25 lines.

Small private header for service fd-set compatibility. In `RUMP_RPC` builds it remaps selected syscalls (`close`, `fcntl`, `read`, `write`, `pollts`, `select`) to rump syscall wrappers.

Under `_LIBC`, it defines `__fd_set_256`, the fixed-size compatibility fdset type used by `rpc_commondata.c` for the exported legacy `svc_fdset`.
