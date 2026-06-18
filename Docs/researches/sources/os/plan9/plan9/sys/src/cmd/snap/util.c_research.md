# File Research: sources/os/plan9/plan9/sys/src/cmd/snap/util.c

Allocation helpers for snap.

Key behavior:
- `emalloc()` allocates and zeroes memory or exits.
- `erealloc()` reallocates or exits.
- `estrdup()` duplicates strings or exits.

Important details:
- Errors are fatal and print `out of memory`.

Filesystem relevance:
- None directly; shared utility support.
