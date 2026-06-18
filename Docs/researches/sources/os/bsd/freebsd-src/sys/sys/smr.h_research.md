# File Research: sources/os/bsd/freebsd-src/sys/sys/smr.h

Safe Memory Reclamation synchronization API.

Key responsibilities:
- Defines modular sequence comparison helpers for wrapping SMR sequence numbers.
- Defines shared SMR state `struct smr_shared` and per-CPU state `struct smr`.
- Defines flags `SMR_LAZY` and `SMR_DEFERRED`.
- Provides inline readers: `smr_enter()`, `smr_exit()`, `smr_lazy_enter()`, and `smr_lazy_exit()`.
- Declares writer/coordination operations: `smr_advance()`, `smr_poll()`, `smr_wait()`, `smr_synchronize()`, `smr_create()`, `smr_destroy()`, and `smr_init()`.

Important patterns:
- Readers record the current write sequence in per-CPU state while in a critical section.
- Writers advance a sequence and wait or poll until all readers have observed the goal.
- Non-lazy SMR uses stronger ordering, including architecture-specific optimization on x86 via locked atomic add.
- Lazy SMR lowers reader overhead in exchange for higher reclamation latency.
- Recursive SMR read sections are explicitly rejected.

Research relevance:
- Core primitive for lockless read-mostly kernel structures that need delayed freeing.
