# File Research: sources/os/plan9/plan9/sys/src/lib9p/mem.c

This file provides fatal allocation helpers for lib9p.

Key behavior:
- `emalloc9p` allocates zeroed memory or exits with `"mem"`.
- `erealloc9p` reallocates memory or exits with `"mem"`.
- `estrdup9p` duplicates strings or exits with `"mem"`.

Notable details:
- Uses Plan 9 allocation tagging helpers `setmalloctag` and `setrealloctag`.
- Callers do not need to check for allocation failure because these helpers terminate on failure.
