# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/epoll.h

## Role

`epoll.h` exposes the illumos epoll compatibility ABI. It defines the Linux-compatible `epoll_data_t` union, packed `struct epoll_event`, event constants, control operation constants, close-on-exec flag, and userland prototypes.

## ABI Details

- `epoll_data_t` can carry a pointer, file descriptor, 32-bit value, or 64-bit value.
- `epoll_event_t` contains a 32-bit event mask plus user data. Conditional `#pragma pack(4)` preserves 32-bit ABI layout on platforms where native long-long alignment differs.
- Event constants intentionally match Linux values and map to poll equivalents where applicable: `EPOLLIN`, `EPOLLPRI`, `EPOLLOUT`, `EPOLLRDNORM`, `EPOLLRDBAND`, `EPOLLWRNORM`, `EPOLLWRBAND`, `EPOLLERR`, `EPOLLHUP`, `EPOLLRDHUP`, plus `EPOLLMSG`.
- High-bit flags are defined for `EPOLLEXCLUSIVE`, ignored `EPOLLWAKEUP`, `EPOLLONESHOT`, and edge-triggered `EPOLLET`.
- Defines `EPOLL_CTL_ADD`, `EPOLL_CTL_DEL`, `EPOLL_CTL_MOD`, and Linux-compatible `EPOLL_CLOEXEC`.

## Userland Surface

Outside the kernel, it declares `epoll_create()`, `epoll_create1()`, `epoll_ctl()`, `epoll_wait()`, and `epoll_pwait()`.
