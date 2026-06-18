# File Research: sources/os/bsd/freebsd-src/sys/sys/sockopt.h

Kernel-only socket option request wrapper.

Key responsibilities:
- Rejects non-kernel inclusion.
- Defines `enum sopt_dir` for get versus set operations.
- Defines `struct sockopt`, carrying direction, level, option name, value pointer, value size, Capsicum rights, and calling thread.
- Declares `sosetopt()`, `sogetopt()`, copyin/copyout helpers, mbuf copy helpers, accept-filter get/set handlers, and `so_setsockopt()` convenience wrapper.

Important patterns:
- `sockopt` abstracts both userspace-originated and kernel-originated socket option handling.
- Copy helpers centralize length validation and transfer between user/kernel buffers or mbufs.
- Capsicum rights are carried with the option operation for descriptor-sensitive options.

Research relevance:
- Kernel-internal boundary for implementing `getsockopt(2)` and `setsockopt(2)` safely and consistently.
