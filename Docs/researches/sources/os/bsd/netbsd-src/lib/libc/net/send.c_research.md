# File Research: sources/os/bsd/netbsd-src/lib/libc/net/send.c

Small compatibility wrapper for `send()`. It implements `send(s, msg, len, flags)` as `sendto(s, msg, len, flags, NULL, 0)` and exports the weak alias for libc namespace handling.

There is no independent socket-send implementation here.
