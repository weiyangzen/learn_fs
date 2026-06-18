# File Research: sources/os/plan9/9front/sys/src/cmd/snap/util.c

Purpose: Allocation helpers for `snap`.

Functions:
- `emalloc`: malloc plus zero-fill, fatal on failure.
- `erealloc`: realloc, fatal on failure except zero-size.
- `estrdup`: strdup, fatal on failure.

Integration: Used across snapshot capture, read, write, and filesystem replay.

Risks: Fatal-on-OOM behavior simplifies callers but makes partial recovery impossible.
