# File Research: sources/os/plan9/plan9/sys/src/9/teg2/l.s

Main ARMv7/Tegra2 low-level assembly for early boot, secondary CPU startup, CP15 accessors, cache/MMU helpers, interrupt-level primitives, and atomic lock support.

Key behavior:
- `_start` enters from U-Boot or another kernel with MMU off, initializes CPU0, builds early L1 mappings, enables caches/MMU, warps into `KZERO`, and calls `main`.
- Nonzero CPUs wait with `WFI` until `cpus_proceed`, then run `cpureset`.
- `cpureset` initializes secondary CPUs, installs per-CPU page tables, enables MMU, and calls `cpustart`.
- Provides address conversion helpers, `setmach`, memory diagnostics, cache-line operations, TLB invalidation, CP15 register get/set functions, `splhi/spllo/splx`, labels, `wfi`, and `coherence`.
- Implements `tas` using ARM `LDREX/STREX`.

Notes:
- Boot prints characters directly for progress diagnostics.
- Comments document ordering constraints around SCU, L1/L2 caches, SMP mode, and MMU transitions.
