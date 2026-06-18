# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/killpg.c

## Scope

Compatibility implementation of `killpg()`.

## Behavior

- Rejects process group `1` and values `<= INT_MIN` with `errno = ESRCH`.
- Sends signals by calling `kill(-pgid, sig)`.

## Dependencies And Invariants

- Uses negative PID semantics of `kill()` for process-group signaling.
- Guards against invalid negation and special process group behavior.
