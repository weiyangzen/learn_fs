# File Research: sources/os/plan9/plan9/sys/src/cmd/faces/util.c

Memory allocation helpers for `faces`.

Key behavior:
- `emalloc()` allocates and zeroes memory or exits on failure.
- `erealloc()` reallocates or exits on failure.
- `estrdup()` duplicates a string or exits on failure.

Risks and invariants:
- These helpers terminate the whole process rather than propagating allocation failures.
- `estrdup()` logs only the first ten characters of the failed source string.
