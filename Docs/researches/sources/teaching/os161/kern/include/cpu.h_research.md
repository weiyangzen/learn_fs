# File Research: sources/teaching/os161/kern/include/cpu.h

Defines per-CPU state and CPU/IPI interfaces.

Key structures:
- `struct cpu` tracks identity, current thread, zombie list, hardclock count, held spinlocks, run queue, idle flag, IPI state, TLB shootdown queue, and optional deadlock-detection actor.

Key APIs:
- CPU creation/init/hatch/start, identify, IRQ on/off, idle/halt.
- IPI send/broadcast/TLB shootdown and interrupt dispatch.
- IPI codes include panic, offline, unidle, and TLB shootdown.

Relevance:
- Provides the concurrency substrate beneath VFS biglock, spinlocks, and thread scheduling.
