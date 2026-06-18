# File Research: sources/os/bsd/netbsd-src/lib/libc/thread-stub/Makefile.inc

## Purpose
Adds libc's non-libpthread thread stub sources.

## Key Elements
Sets `.PATH` to `thread-stub` and adds `__isthreaded.c`, `thread-stub.c`, and `thread-stub-init.c`.

## Dependencies
Includes `<bsd.own.mk>` and depends on libc's thread-stub directory.

## Behavior/Risks
Build-only file; these stubs are included so libc can satisfy weak thread hooks when libpthread is absent.
