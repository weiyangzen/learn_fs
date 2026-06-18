# File Research: sources/os/bsd/netbsd-src/lib/libedit/readline/Makefile

## Purpose
Installs libedit's readline-compatible public headers.

## Main Behavior
Declares `NOOBJ`, includes NetBSD build ownership rules, sets `.PATH` to `${NETBSDSRCDIR}/lib/libedit`, installs `readline.h` into `/usr/include/readline`, and creates `history.h` as a symlink to `readline.h`.

## Dependencies
Uses NetBSD make infrastructure: `<bsd.own.mk>` and `<bsd.prog.mk>`.

## Risks And Notes
This directory builds no objects. Its role is header installation and compatibility layout for consumers expecting `<readline/readline.h>` and `<readline/history.h>`.
