# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_ntop.c

Implements standard `inet_ntop`.

Behavior:
- Dispatches `AF_INET` to `inet_ntop4` and `AF_INET6` to `inet_ntop6`.
- IPv4 formats `a.b.c.d` with `snprintf`, returning `ENOSPC` if too small.
- IPv6 converts bytes to 16-bit words, finds the longest zero run for `::`, handles embedded IPv4, and checks output buffer size before copying.
- Unsupported families set `EAFNOSUPPORT`.

Does not use static storage; caller supplies output buffer.
