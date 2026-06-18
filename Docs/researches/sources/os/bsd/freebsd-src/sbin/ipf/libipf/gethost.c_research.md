# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/gethost.c

This helper resolves a hostname/network name into an `i6addr_t`.

For IPv4, `gethost()` first recognizes the special test name `test.host.dots`, then replaces `<thishost>` with global `thishost`, tries `gethostbyname()`, and falls back to `getnetbyname()`. For IPv6 builds, it uses `getaddrinfo()` with `PF_INET6`.

It zeroes the output address before resolution and returns `0` on success or `-1` on failure.

Implementation note: the IPv6 branch does not check the return value of `getaddrinfo()` before testing `res`, so correctness relies on `res` being set appropriately.
