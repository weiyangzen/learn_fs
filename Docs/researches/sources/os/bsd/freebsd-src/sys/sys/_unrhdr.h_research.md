# File Research: sources/os/bsd/freebsd-src/sys/sys/_unrhdr.h

Unit number allocator header structure.

Key elements:
- Defines `struct unrhdr` with allocation range, busy/allocation counts, first/last free tracking, mutex pointer, main TAILQ, and deferred-free TAILQ.

Dependencies:
- Includes `sys/queue.h`.
- Forward-declares `struct mtx`.

Research notes:
- Used by kernel subsystems that allocate stable numeric IDs.
- Deferred-free queue supports freeing after dropping the allocator lock.
