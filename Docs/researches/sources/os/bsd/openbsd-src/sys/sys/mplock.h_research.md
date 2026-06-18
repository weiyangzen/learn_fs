# File Research: sources/os/bsd/openbsd-src/sys/sys/mplock.h

Defines the machine-independent MP kernel lock interface when enabled by machine headers.

Key contents:
- Includes `<machine/mplock.h>`.
- Under `__USE_MI_MPLOCK`, defines per-CPU ticket/depth tracking and `struct __mp_lock`.
- Optional WITNESS lock object integration.
- Extern global `kernel_lock`.

Key APIs:
- `___mp_lock_init`, `__mp_lock`, `__mp_unlock`, `__mp_release_all`, `__mp_acquire_count`, `__mp_lock_held`.
- `__mp_lock_init` macro wraps WITNESS naming when enabled.

Risk notes:
- Recursion/depth and per-CPU ticket state are central to legacy kernel-lock correctness.
