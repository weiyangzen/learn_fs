# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/aux.c

This file provides small allocation helpers for the flashfs code.

Key behavior:
- `emalloc9p` allocates zeroed memory or exits on failure.
- `erealloc9p` reallocates or exits on failure.
- `estrdup9p` duplicates a string or exits on failure.

Important details:
- Sets Plan 9 malloc/realloc tags from caller PCs.
- Error messages go to stderr and terminate the process with `"mem"`.

Filesystem relevance:
- Supporting utility for flashfs and its bundled 9P service code.
