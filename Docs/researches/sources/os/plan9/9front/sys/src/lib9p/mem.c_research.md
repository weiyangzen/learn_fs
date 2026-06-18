# File Research: sources/os/plan9/9front/sys/src/lib9p/mem.c

## Read Status
Complete: 42 lines read.

## Purpose
Provides fatal-on-failure allocation helpers for lib9p.

## Main Responsibilities
- Allocate zeroed memory.
- Reallocate memory with fatal error handling.
- Duplicate strings with fatal error handling.
- Set Plan 9 allocation/reallocation tags for debugging.

## Important Functions
- `emalloc9p`: `malloc`, zero-fill, tag, or `sysfatal`.
- `erealloc9p`: `realloc`, tag, or `sysfatal`.
- `estrdup9p`: `strdup`, tag, or `sysfatal`.

## Dependencies and Interactions
- Used throughout lib9p for simpler error paths.
- Allocation failures terminate the process rather than returning errors.
