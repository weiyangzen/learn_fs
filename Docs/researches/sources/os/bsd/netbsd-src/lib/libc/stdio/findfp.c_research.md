# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/findfp.c

Read completely: 228 lines.

This file owns stdio stream allocation and initialization. It defines the standard `__sF[3]` streams, extension objects, the initial static `usual` stream pool, the glue-list allocator `moreglue`, `__sfpinit`, `__sfp`, `f_prealloc`, `_cleanup`, and `__sinit`.

Important interactions: every `fopen`-style function obtains a `FILE` via `__sfp`; `_cleanup` flushes all streams on process exit; `_fwalk` traverses the glue list.

Security/reliability notes: stream allocation is protected by `__sfp_lock` in reentrant builds. `f_prealloc` can allocate many `FILE` slots based on `_SC_OPEN_MAX`.
