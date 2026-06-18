# File Research: sources/os/plan9/9front/sys/src/9/bcm/armv7.s

Cortex-A7/ARMv7 boot, SMP startup, atomics, and low-level machine support.

Key behavior:
- CPU 0 performs primary boot: enters SVC from possible HYP mode, disables caches/MMU, clears tables, initializes MMU, enables SMP/coherency, caches, MMU, and high vectors.
- Secondary CPUs enter through `cpureset`, locate their `Mach`, install per-CPU page table base, enable MMU/caches, and call `cpustart`.
- Handles HYP-to-SVC transition with `ERET`.
- Provides CP15 accessors, cycle read, spl helpers, LDREX/STREX `cmpswap` and `tas`, labels, idle WFI, barriers, SEV, and TLB invalidation.
- Provides cache line range operations and includes `cache.v7.s` for whole-cache operations.

Dependencies:
- Includes `arm.s` and `cache.v7.s`.
- Calls `mmuinit`, `mmuinvalidate`, `main`, and `cpustart`.

Research notes:
- Explicitly toggles SMP bit in auxiliary control before and after early cache/MMU setup.
