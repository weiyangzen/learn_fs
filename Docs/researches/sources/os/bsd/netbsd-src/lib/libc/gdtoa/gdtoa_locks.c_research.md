# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/gdtoa_locks.c

Purpose: Provides global locks for gdtoa in threaded NetBSD libc builds.

Core behavior:
- Defines `mutex_t __gdtoa_locks[2]` only when `_REENTRANT` is enabled.
- The two locks protect Bigint freelists/private allocation and lazy powers-of-five cache construction.

Dependencies:
- Includes `gdtoaimp.h`, which maps `ACQUIRE_DTOA_LOCK` and `FREE_DTOA_LOCK` to these locks under `MULTIPLE_THREADS`.
