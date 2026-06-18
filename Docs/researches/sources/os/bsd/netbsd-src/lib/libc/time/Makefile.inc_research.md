# File Research: sources/os/bsd/netbsd-src/lib/libc/time/Makefile.inc

## Purpose
Integrates selected tzcode time functions into NetBSD libc.

## Key Elements
Adds `asctime.c`, `difftime.c`, `localtime.c`, `getdate.c`, `strftime.c`, and `strptime.c`; adds related man pages; sets `CPPFLAGS` for `USG_COMPAT` and `SUPPORT_POSIX2008`; and declares extensive `MLINKS`.

## Dependencies
Uses `.PATH` for `${.CURDIR}/time`, libc build variables, and `COPTS.strftime.c`.

## Behavior/Risks
Build-only integration file; exported API coverage depends on matching NetBSD man links and tzcode feature macros.
