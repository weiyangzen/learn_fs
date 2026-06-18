# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/inet_addr.c

This is a compatibility implementation of BSD `inet_aton()`.

It parses IPv4 textual forms using decimal, octal, and hexadecimal components, supporting historical `a`, `a.b`, `a.b.c`, and `a.b.c.d` forms. It validates component bounds, rejects trailing non-space characters, assembles the address in host order, and stores network byte order in `addr->s_addr`.

A compatibility `inet_addr()` implementation is present but disabled with `#if 0`.

The file includes BSD/DEC license text and safe ctype wrapper macros for unsigned-char casting.
