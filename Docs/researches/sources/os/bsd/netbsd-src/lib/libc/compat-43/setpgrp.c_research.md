# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/setpgrp.c

## Scope

Compatibility implementation of two-argument `setpgrp()`.

## Behavior

- Calls `setpgid(pid, pgid)` and returns its result.

## Dependencies And Invariants

- Preserves old BSD API shape while delegating to POSIX process-group control.
