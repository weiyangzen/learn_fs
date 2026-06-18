# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_devstat.c

Kernel device I/O statistics registry and transaction accounting implementation.

Key responsibilities:
- Maintains a priority-sorted global `devstat` singly-linked tail queue.
- Adds/removes `devstat` entries, assigning stable device numbers, creation time, block size, support flags, type flags, and priority.
- Tracks transaction start and completion, including busy periods, read/write/free/other operation counts, byte counters, completion time, and ordered tag counters.
- Provides `devstat_end_transaction_buf()` to classify completed `struct buf` commands.
- Exports all device statistics, generation, number of devices, and devstat ABI version through `kern.devstat.*` sysctls.

Important behavior:
- `busy_count` is atomically incremented/decremented; busy time is accumulated only when the device transitions back to idle.
- The `kern.devstat.all` sysctl emits the generation number followed by the current array of `struct devstat` entries to keep the snapshot self-consistent for userland.

Dependencies:
- Depends on DragonFly buffer command values, sysctl, timekeeping, and `sys/devicestat.h`.

Notable risks:
- The global devstat queue and generation counters have no explicit lock in this file; callers rely on higher-level registration discipline.
- Per-device byte and operation counters are plain fields, so concurrent updates may be approximate rather than strictly serialized.
- If `devstat_end_transaction()` is called more times than start, it logs a negative `busy_count` warning but does not otherwise repair accounting.
