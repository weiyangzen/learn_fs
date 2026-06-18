# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/compat.c

Compatibility layer that lets selected Plan 9 kernel-style device code run in user space.

Key responsibilities:
- Initializes per-process `Proc` state through `privalloc()` and `newup()`.
- Spawns kernel-style processes with `rfork(RFPROC|RFMEM|RFNOWAIT)`.
- Implements `panic`, `smalloc`, `seconds`, `error`, `nexterror`, and `readstr`.
- Provides Plan 9-style `Rendez` sleep/wakeup using `rendezvous()`.
- Supports interrupting sleeps through `rendintr()` and clearing pending interrupts.
- Tracks and validates error-stack depth.

Important behavior:
- `waserror()`/`poperror()` are implemented in the header using `setjmp`/`longjmp`.
- `openmode()` maps `OEXEC` to `OREAD` and rejects invalid modes.
- `initcompat()` also installs a rendezvous namespace with `rfork(RFREND)`.

Risks:
- Rendezvous uses sentinel values and panics on unexpected pairings.
- Shared-memory forked processes rely on per-process `up` but shared global device state.
