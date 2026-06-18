# File Research: sources/os/bsd/dragonflybsd/sys/sys/single_threaded.h

This user ABI header declares libc threading-state globals.

Key responsibilities:
- Declares `extern int __isthreaded` once via `__LIBC_ISTHREADED_DECLARED`.
- Declares `extern char __libc_single_threaded`.

Important invariants:
- Comment states zero value of `__libc_single_threaded` indicates the process might be multi-threaded.
- The header uses C linkage guards through `__BEGIN_DECLS`/`__END_DECLS`.

Research notes:
- This header exposes libc runtime state used by optimized single-threaded code paths.
