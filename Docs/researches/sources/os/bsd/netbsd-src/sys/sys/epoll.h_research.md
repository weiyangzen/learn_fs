# File Research: sources/os/bsd/netbsd-src/sys/sys/epoll.h

Defines NetBSD’s Linux-compatible epoll API constants, structures, and declarations.

Key content:
- `EPOLL_CLOEXEC` aliases `O_CLOEXEC`.
- Event flags: `EPOLLIN`, `EPOLLPRI`, `EPOLLOUT`, `EPOLLERR`, `EPOLLHUP`, normal/band read/write, message, read-half-hup, wakeup, oneshot, edge-triggered.
- Control operations: add, delete, modify.
- Kernel max events: `EPOLL_MAX_EVENTS`.
- Kernel `epoll_data_t` as `uint64_t`; userland `union epoll_data`.
- `struct epoll_event`.
- Kernel common implementations: `epoll_ctl_common`, `epoll_wait_common`.
- Userland declarations under `_NETBSD_SOURCE`: `epoll_create`, `epoll_create1`, `epoll_ctl`, `epoll_wait`, `epoll_pwait`, `epoll_pwait2`.

Important behavior:
- Bridges Linux API semantics into NetBSD’s kernel/user ABI.
- Uses feature-test gating for public function declarations.
