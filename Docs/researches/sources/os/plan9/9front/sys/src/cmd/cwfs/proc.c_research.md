# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/proc.c

Purpose: Small process-spawning wrapper for cwfs.

Key behavior:
- `newproc()` forks with `RFPROC|RFMEM|RFNOWAIT`.
- In the child, it sets the process name with `procsetname()`, invokes the supplied function, and exits with `"child returned"` if the function returns.
- Parent continues immediately.

Notable details:
- `RFMEM` means worker processes share memory, matching cwfs’s lock-based shared-state design.
