# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/data.c

Global kernel-facade data definitions for drawterm.

Key contents:
- Defines `Proc *up`.
- Initializes `conf` with one machine, 100 processes, large default page/memory/cache-like limits, and zero UARTs.
- Defines default user `eve`, `kerndate`, `cpuserver`, and `hostdomain`.

Role in this group:
- Supplies global state referenced throughout the drawterm kernel and device layer.

Notable risks:
- `up` is also macro-defined through `_getproc()` in `dat.h`; this definition is legacy/global state and must match surrounding build expectations.
- Large fixed defaults are coarse and not tied to actual host resources.
