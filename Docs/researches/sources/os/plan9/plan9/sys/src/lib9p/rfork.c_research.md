# File Research: sources/os/plan9/plan9/sys/src/lib9p/rfork.c

This file provides process-based serving wrappers for lib9p.

Key behavior:
- Defines `rforker`, which starts a function in a new process using `rfork(RFPROC|RFMEM|RFNOWAIT|flag)`.
- Child processes run the supplied function and call `_exits(0)`.
- `listensrv` sets global `_forker` to `rforker` and delegates to `_listensrv`.
- `postmountsrv` sets `_forker` to `rforker` and delegates to `_postmountsrv`.

Role:
- Selects process/rfork concurrency for listening and postmount serving.
- Complements `thread.c`, which selects libthread process creation instead.
