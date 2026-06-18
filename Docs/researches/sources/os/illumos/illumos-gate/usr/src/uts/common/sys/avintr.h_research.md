# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/avintr.h

This header defines kernel autovectored interrupt and soft interrupt data structures and registration/removal prototypes.

Key contents:
- Interrupt constants `MAXIPL`, `INT_IPL(x)`, and `AV_INT_SPURIOUS`.
- Interrupt function type `avfunc`.
- `struct autovec`: linked interrupt handler entry with vector, two args, tick counter pointer, priority, interrupt id, device info pointer, flags, and IPL chain link.
- `AV_PENTRY_*` pending/servicing/level-trigger flag masks.
- `struct av_head` for interrupt chain priority bounds.
- `struct softint` with pending software interrupt bitfield.
- Kernel-only globals and functions for adding/removing hardware, NMI, and software interrupt handlers, moving soft interrupt priority, updating args, waiting for visibility, and `softlevel1`.

Dependencies:
- Includes `sys/mutex.h`, `sys/dditypes.h`, and `sys/ddi_intr.h`.
- Kernel-only operational declarations are under `_KERNEL`.

Research notes:
- Internal kernel interrupt infrastructure; not a user ABI.
- Registration functions identify handlers by interrupt id, IPL, vector/function, and vector number depending on path.
