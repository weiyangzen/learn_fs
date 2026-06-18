# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Makefile.inc

Build fragment for libc string sources. It adds generic string, memory, bstring, popcount, secure-memory, byte-search, and wide-character source files to `SRCS`, sets include paths for locale-dependent wide comparisons, disables builtin generation for `memset.c`, and includes the architecture-specific string `Makefile.inc`.

It also registers manual pages and MLINK aliases for legacy names, wide functions, popcount variants, and related APIs.
