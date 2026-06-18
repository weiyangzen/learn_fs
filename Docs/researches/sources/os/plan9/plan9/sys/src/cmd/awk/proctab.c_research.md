# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/proctab.c

Generated dispatch table for the awk interpreter.

Contains:

- `printname[92]`: token names for debugging.
- `proctab[92]`: maps token offsets from `FIRSTTOKEN` to runtime function pointers.
- `tokname()`: returns token names or a fallback formatted token number.

Expression/statement execution in `run.c` depends on this table. Tokens without runtime behavior map to `nullproc`.
