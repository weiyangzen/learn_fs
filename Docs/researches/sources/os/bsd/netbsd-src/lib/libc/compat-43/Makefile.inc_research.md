# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/Makefile.inc

## Scope

Build fragment for libc 4.3BSD compatibility sources.

## Behavior

- Adds `compat-43` source search paths for architecture-specific and common compatibility code.
- Adds `creat.c`, `getdtablesize.c`, `gethostid.c`, `killpg.c`, `sethostid.c`, `setpgrp.c`, `setrgid.c`, `setruid.c`, and `sigcompat.c`.
- Adds `getwd.c` unless `AUDIT` is defined.
- Adds include path for `<compat/sys/signal.h>` when compiling `sigcompat.c`.
- Registers manual pages and mlinks for related compatibility APIs.

## Dependencies And Invariants

- Depends on NetBSD make variables such as `ARCHDIR`, `.CURDIR`, `NETBSDSRCDIR`, `SRCS`, `MAN`, and `MLINKS`.
