# File Research: sources/os/plan9/9front/sys/src/cmd/9l/cputime.c

This file provides hosted compatibility helpers for timing and file creation/seek behavior.

Key routines:
- `cputime` sums process CPU time from `times` and returns seconds as a double.
- `seek` wraps `lseek`.
- `create` wraps Unix `creat`, accepting only mode argument `m == 1`.

Important interactions:
- Used by verbose linker timing logs in files such as `obj.c`, `asm.c`, `pass.c`, and `span.c`.
- Provides Plan 9-like function names in a hosted environment.

Research notes:
- This is support glue, not target-specific linker logic.
