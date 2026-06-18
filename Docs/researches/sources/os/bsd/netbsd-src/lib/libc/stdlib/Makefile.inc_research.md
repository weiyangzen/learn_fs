# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/Makefile.inc

Read completely: 117 lines.

Build fragment for libc stdlib sources. It adds environment, random, conversion, search, sort, allocation, process, and string-to-number files to `SRCS`, includes architecture-specific stdlib rules, and conditionally selects external jemalloc, in-tree `jemalloc.c` plus `aligned_alloc.c`, or legacy `malloc.c`.

It also declares manpages and `MLINKS` for stdlib APIs, generates `strtou.3` from `strtoi.3` with `sed`, and adds a lint flag workaround for `strfmon.c`. This file is the main build switchboard for the stdlib portion of NetBSD libc.
