# File Research: sources/os/bsd/netbsd-src/lib/libcompat/Makefile

## Purpose
Builds NetBSD `libcompat`, a library of older BSD/libc compatibility APIs.

## Build Behavior
Sets `LIB=compat`, compatibility CPP flags, assembler include paths, and `.PATH` for 4.1, 4.3, 4.4, machine-specific, and regexp sources. Builds 4.1 APIs (`gtty`, `ftime`, `stty`), 4.3 APIs (`cfree`, `regex`, `rexec`, `ruserpass`), 4.4 `cuserid`, and regexp sources (`regexp.c`, `regsub.c`). Installs related manpages and links.

## Dependencies
Depends on NetBSD make infrastructure, libc architecture include directories, optional `DESTDIR`, and source files under compatibility version subdirectories.

## Risks And Notes
This library deliberately preserves obsolete interfaces. The makefile documents several missing historical sources, so compatibility coverage is selective rather than complete.
