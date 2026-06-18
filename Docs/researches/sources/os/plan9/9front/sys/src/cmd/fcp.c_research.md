# File Research: sources/os/plan9/9front/sys/src/cmd/fcp.c

## Purpose
Parallel file copy utility with optional metadata preservation.

## Key Elements
Accepts `-g`, `-u`, and `-x` metadata flags; validates destination directory usage; rejects directories and same-file copies; creates destination with source mode; spawns up to eight shared-memory worker processes; assigns offsets through a `QLock`-protected global counter; copies using `pread`/`pwrite`; and optionally wstats mtime, mode, uid, and gid.

## Dependencies
Uses Plan 9 `Dir`, `rfork(RFPROC|RFMEM)`, `wait`, notes, `iounit`, and `dirfwstat`.

## Behavior/Risks
Parallel writes assume the destination supports positional writes correctly. Worker allocation failure exits success-like via `_exits(nil)` after printing an error, so the parent may not treat that specific failure as copy failure.
