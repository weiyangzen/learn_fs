# File Research: sources/os/bsd/netbsd-src/lib/libc/net/recv.c

Small compatibility wrapper for `recv()`. It implements `recv(s, buf, len, flags)` as `recvfrom(s, buf, len, flags, NULL, NULL)`.

There is no independent syscall logic or buffering in this file.
