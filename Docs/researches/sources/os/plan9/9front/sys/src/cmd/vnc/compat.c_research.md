# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/compat.c

## Role

`compat.c` supplies user-space replacements for Plan 9 kernel services used by the VNC server's transplanted device code.

## Main Services

- Initializes process-local `up`, `eve`, rendezvous state, and kernel date with `initcompat()`.
- Provides `newup()` and `kproc()` to create kernel-like process records for child processes.
- Implements `panic()`, `smalloc()`, `seconds()`, `error()`, `nexterror()`, and `readstr()`.
- Maps open modes with `openmode()`.
- Implements `Rendez` sleep/wakeup with Plan 9 `rendezvous()` and interrupt state in `Proc`.
- Provides `rendintr()` and `rendclearintr()` for interrupting blocking pseudo-kernel sleeps.
- Tracks `waserror()` nesting through `errdepth()`.

## Notable Limitations And Risk Areas

- `kproc()` uses `rfork(RFPROC|RFMEM|RFNOWAIT)`, so child processes share memory and require careful locking.
- Error handling depends on `up` being initialized per process before any `waserror()`/`error()` usage.
- Rendezvous code uses sentinel values and panics on mismatches except for the global interrupt tag case.
- `panic()` exits the process instead of attempting recovery.
