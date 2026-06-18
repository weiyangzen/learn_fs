# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/posix.c

This file is the POSIX host runtime shim for drawterm's Plan 9-like kernel process model.

Key behavior:
- Stores the current `Proc*` in a pthread key via `_getproc` and `_setproc`.
- `osinit` initializes TLS and installs a `SIGPIPE` ignore handler.
- `osnewproc`, `osproc`, and `tramp` create pthread-backed kernel processes and run `Proc.kpfun`.
- `procsleep` and `procwakeup` block/wake a hosted process using `pthread_cond_t`.
- `oserror`/`oserrstr` translate host `errno` into Plan 9 error strings.
- `randomread`, `seconds`, `ticks`, `osmsleep`, and `osyield` provide host services.

Important details:
- `osnewproc` initializes each `Proc` with a private mutex and condition variable.
- Random data comes from `/dev/urandom` unless `USE_RANDOM` forces libc `random()`.
- `showfilewrite` is a no-op stub for hosted control files.
