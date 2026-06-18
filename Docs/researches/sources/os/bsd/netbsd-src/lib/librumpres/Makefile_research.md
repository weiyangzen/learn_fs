# File Research: sources/os/bsd/netbsd-src/lib/librumpres/Makefile

Read completely: 28 lines.

## Purpose
Builds `librumpres`, the rump resolver support library using selected libc network-name service sources.

## Main Responsibilities
- Enables fortification by default and shared-library installation.
- Disables full RELRO.
- Sets `LIB=rumpres` and shared-library major/minor to `0.0`.
- Depends on `librumpclient`.
- Adds `-DINET6` unless `USE_INET6=no`.
- Builds resolver/interface-name sources from `../libc/net`: `getaddrinfo.c`, `getifaddrs.c`, `getnameinfo.c`, `if_indextoname.c`, and `if_nametoindex.c`.
- Defines `RUMP_ACTION` for those reused libc sources.
- Suppresses stringop-overflow warnings for `getaddrinfo.c`.

## Filesystem Relevance
Low. The library is resolver/network support rather than filesystem logic, but it participates in the rump userland library set used by rump-based systems.

## Dependencies
- `bsd.own.mk` and `bsd.lib.mk`.
- `../librumpclient`.
- Reused libc network source files.
