# File Research: sources/os/plan9/plan9/sys/src/9/bcm/l.s

BCM2835 ARM1176JZF-S low-level boot and machine helper assembly.

Key behavior:
- `_start` enters with MMU off, sets SVC mode with interrupts disabled, disables MMU/caches/prediction, invalidates caches/TLB, clears early Mach/page-table memory, calls `mmuinit()`, installs DAC/TTB, enables MMU/cache/high vectors, then jumps into kernel virtual address space.
- `_startpg` enables the cycle counter and calls `main()`.
- Provides CP15 read helpers for data/instruction fault status, fault address, and cycle counter.
- Implements `splhi`, `splfhi`, `splflo`, `spllo`, `splx`, and `islo`.
- Implements `tas` using `SWPW`, label save/restore, caller PC fetch, idle wait-for-interrupt, coherence barriers, TLB invalidation, and cache writeback/invalidate helpers.
- Range cache operations use ARMv6 `MCRR` cache-range maintenance.

This file is the core execution-mode, interrupt-level, cache, and early-boot assembly support for the BCM kernel.
