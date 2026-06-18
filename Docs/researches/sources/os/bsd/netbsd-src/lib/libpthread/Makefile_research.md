# File Research: sources/os/bsd/netbsd-src/lib/libpthread/Makefile

## Purpose
Builds NetBSD `libpthread`, including machine-dependent thread support and ISO C11 threads wrappers.

## Main Responsibilities
- Selects architecture subdirectory from `PTHREAD_MACHINE_ARCH`, `PTHREAD_MACHINE_CPU`, `MACHINE_ARCH`, or `MACHINE_CPU`.
- Builds export symbol list from MI and MD symbol files.
- Sets libc/threading CPP flags and includes libc internals.
- Prevents libpthread unloading with linker `-z nodelete`.
- Builds core pthread source files, scheduler/cancel/mutex/cond/rwlock/spin/barrier/TSD code, semaphore code from librt, and optional MD assembly.
- Supports `PTHREAD__COMPAT` for NetBSD 2/3/4 chroots on newer kernels.
- Adds C11 thread sources: `call_once.c`, `cnd.c`, `mtx.c`, `thrd.c`, `tss.c`.
- Creates static `libpthread.a` as a single large relocatable object so linking any pthread symbol pulls in all pthread functionality.
- Installs pthread and C11 thread headers and extensive manpage MLINKs.

## Key Implementation Notes
- The file emphasizes that new libpthread source files must be referenced from `pthread.c` to avoid static archive discard.
- Alpha and hppa use MD RAS assembly exports; other architectures export MI RAS symbols.

## Dependencies
- Architecture-specific `arch/*/pthread_md.*`.
- `pthread_int.h`, pthread source modules, libc internals, librt `sem.c`.
