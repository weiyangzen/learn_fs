# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devpoll.h

This header defines `/dev/poll` ioctl ABI and kernel entry bookkeeping. It includes poll implementation and 32-bit type support.

Ioctls under `DPIOC` include `DP_POLL`, `DP_ISPOLLED`, `DP_PPOLL`, and `DP_EPOLLCOMPAT`. `DEVPOLLSIZE` is the table growth increment.

`dvpoll_t` is the user ioctl payload with pollfd array pointer, fd count, timeout in milliseconds, and optional signal set pointer. `dvpoll32_t` is the 32-bit ABI version. `dvpoll_epollfd_t` places `pollfd_t` first and adds a 64-bit epoll-compatible payload.

Kernel-only `dp_entry_t` stores a lock, pollcache pointer, reference count, writer wait count, flags, and cv. Flags track writer presence and epoll compatibility mode. `DP_REFRELE` decrements entry references with an assertion.

Research notes:
- This is a user-visible ABI for `/dev/poll`, including syscall32 layouts.
- The epoll compatibility structure depends on `pollfd_t` being the first member.
- Kernel entry locking protects concurrent ioctl and write/update paths.
