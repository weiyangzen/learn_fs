# File Research: sources/os/bsd/netbsd-src/lib/libresolv/Makefile

Read completely: 28 lines.

Builds NetBSD `libresolv` from resolver support sources shared with libc. It adds libc include/resolver/name-server include paths, defines `_LIBRESOLV`, conditionally enables `INET6`, and sets `.PATH` to libc `net`, `resolv`, and `nameser` directories.

The compiled sources are the dynamic update, TSIG signing/verification, DNS date, zone-cut, DST key, HMAC, and support files in this group plus `ns_samedomain.c`. Commented-out lines document broader libc resolver sources that are intentionally not built into this standalone library.
