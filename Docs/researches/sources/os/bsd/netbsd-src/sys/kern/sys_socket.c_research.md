# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_socket.c

Provides the `fileops` adapter for sockets, making sockets behave as file descriptors for read/write/ioctl/poll/stat/close/kqueue/restart/fpathconf/fadvise paths.

Key structures and entry points:
- `socketops`: file operation table for `DTYPE_SOCKET`.
- `ifioctl`: function pointer for interface ioctl handling, defaulting to `eopnotsupp`.
- `soo_read`: delegates to `so_receive`.
- `soo_write`: delegates to `so_send`.
- `soo_ioctl`: handles socket fd ioctls including nonblocking mode, async mode, read/write byte counts, send buffer space, owner/process group, at-mark query, SCTP peeloff, interface ioctls, and protocol-specific ioctls.
- `soo_poll`: delegates to `sopoll`.
- `soo_stat`: fills `S_IFSOCK` stat data and delegates protocol stat under socket lock.
- `soo_close`: calls `soclose` and clears `f_socket`.
- `soo_restart`: delegates to `sorestart`.
- `soo_fpathconf`: supports `_PC_PIPE_BUF`.
- `soo_posix_fadvise`: returns `ESPIPE`.

Concurrency/locking:
- Uses `solock`/`sounlock` when mutating socket state or querying protocol stat.
- Protocol-specific ioctls run under `KERNEL_LOCK` unless handled by MP-safe interface ioctl path later.

Research notes:
- This is a bridge between generic file descriptor operations and the socket subsystem; it participates in readiness polling through `soo_poll`.
