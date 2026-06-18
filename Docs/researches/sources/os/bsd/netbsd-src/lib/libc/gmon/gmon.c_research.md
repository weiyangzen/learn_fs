# File Research: sources/os/bsd/netbsd-src/lib/libc/gmon/gmon.c

NetBSD libc implementation of `monstartup`, `moncontrol`, and `_mcleanup` for `gprof` profiling output.

Key behavior:
- `monstartup(lowpc, highpc)` rounds text bounds, sizes histogram/from/to arc tables, allocates them with `sbrk`/`brk`, initializes profiling, and starts `profil(2)`.
- `_mcleanup()` stops profiling, determines profiling clock rate with `sysctl(KERN_CLOCKRATE)` or fallback `hertz()`, opens `gmon.out` or `$PROFDIR/<pid>.<progname>`, writes the `gmonhdr`, histogram, and raw call arcs.
- Refuses to write profiling output for setuid/setgid mismatch cases.
- `moncontrol(mode)` starts/stops kernel profiling via `profil`.

Threaded mode:
- `_REENTRANT` builds maintain per-thread `struct gmonparam` instances using thread-specific data.
- `_m_gmon_alloc()` mmaps per-thread arc storage.
- `_m_gmon_destructor()` moves thread data to a free list.
- `_m_gmon_merge()` merges per-thread arcs into the global profile before writing.

Dependencies: `<sys/gmon.h>`, `profil`, `sysctl`, `mmap`, `reentrant.h`, `extern.h` for `__minbrk`.
