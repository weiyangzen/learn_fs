# File Research: sources/os/plan9/9front/sys/src/9/bcm/armv6.s

ARM1176/ARMv6 boot and low-level machine support for BCM2835.

Key behavior:
- Starts in SVC mode with IRQ/FIQ disabled.
- Disables MMU/caches, invalidates caches/TLB, clears Mach/page-table space, initializes page tables, enables MMU/caches/high vectors, and jumps to virtual `main`.
- Enables the ARM1176 cycle counter.
- Provides CP15 fault/status/id accessors, cycle counter read, spl helpers, test-and-set via SWP, labels, idle wait, barriers, TLB invalidation, and cache maintenance.
- Provides range and whole-cache operations using ARMv6 cache maintenance instructions.

Dependencies:
- Includes `arm.s`, `mem.h`, and `arm.h`.
- Calls `mmuinit` and `main`.

Research notes:
- L2 cache operations are stubs because this target does not enable L2 cache.
