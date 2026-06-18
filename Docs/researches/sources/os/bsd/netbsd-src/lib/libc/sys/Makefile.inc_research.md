# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/Makefile.inc

## Purpose
Builds the NetBSD libc system-call wrapper layer, including architecture-specific assembly stubs, C compatibility glue, lint stubs, and syscall manual-page links.

## Key Elements
Adds syscall wrapper sources such as `accept4.c`, `sched.c`, `sigwait.c`, `statvfs.c`, and time/offset compatibility glue. It generates assembly stubs from `SYS.h` using `RSYSCALL`, `PSEUDO`, `PSEUDO_NOERROR`, `WSYSCALL`, and related macros; creates lint files with `makelintstub`; and declares extensive `MAN`/`MLINKS` mappings.

## Dependencies
Depends on `${ARCHDIR}/sys`, `${.CURDIR}/sys`, `${DESTDIR}/usr/include/sys/syscall.h`, `${ARCHDIR}/SYS.h`, `makelintstub`, make conditionals such as `RUMPRUN`/`MKLINT`, and generated temporary assembly targets.

## Behavior/Risks
The file encodes ABI compatibility details for old 64-bit offset padding, `*50` time syscalls, no-error syscalls, pseudo syscalls, weak syscall aliases, and architecture overrides. Build correctness depends on generated names matching syscall headers and on architecture-specific `.S` files taking precedence over default C glue.
