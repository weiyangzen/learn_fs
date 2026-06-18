# File Research: sources/os/bsd/freebsd-src/sbin/restore/utilities.c

Purpose: filesystem operation helpers and diagnostics used across restore.

Key functions:
- `pathcheck()` ensures parent directory entries exist in the symbol table and creates missing directories when extracting by name.
- `mktempname()` and `gentempname()` generate and apply collision-safe temporary names for rename/deletion choreography.
- `renameit()`, `newnode()`, `removenode()`, `removeleaf()`, `linkit()`, `addwhiteout()`, and `delwhiteout()` perform filesystem mutations with `Nflag` dry-run support.
- `lowerbnd()` and `upperbnd()` locate the next/last inode needing extraction.
- `badentry()`, `flagvalues()`, `dirlookup()`, `reply()`, and `panic()` provide diagnostics, prompting, and recoverable/fatal consistency handling.

Integration: called by restore reconciliation, extraction, directory mode replay, and interactive selection. It is the abstraction layer between symbol-table decisions and live filesystem effects.

Risk notes: helpers often continue after filesystem warnings to support best-effort restore. `panic()` returns instead of exiting when `yflag` is set, so callers must tolerate continuing after inconsistencies.
