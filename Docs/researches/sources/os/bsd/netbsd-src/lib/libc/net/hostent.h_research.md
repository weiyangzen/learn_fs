# File Research: sources/os/bsd/netbsd-src/lib/libc/net/hostent.h

Internal header for NetBSD host database reentrant helpers. It declares non-standard `sethostent_r()`, `gethostent_r()`, `endhostent_r()`, `gethostbyname*_r()`, and `gethostbyaddr_r()` interfaces used inside libc to provide thread-safe host lookups.

It also exposes internal test hooks for `/etc/hosts`, DNS, and optional NIS host lookups, plus buffer-packing macros `HENT_ARRAY`, `HENT_COPY`, and `HENT_SCOPY`. `MAXALIASES` and `MAXADDRS` are fixed at 35.
