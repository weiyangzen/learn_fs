# File Research: sources/os/plan9/9front/sys/src/9/teg2/l.s

Tegra 2 ARMv7 bootstrap and low-level machine support.

Purpose:
- Starts CPU0 from U-Boot or another Plan 9 kernel with the MMU off.
- Parks secondary CPUs until `cpus_proceed`, then starts them through `cpureset`.
- Builds early L1 section mappings for DRAM and MMIO, enables caches/MMU, warps execution into `KZERO`, then calls `main`.

Key behavior:
- Contains early serial progress output, memory diagnostic probing, Mach setup, physical/virtual address conversion, and `setmach`.
- Provides cache-line maintenance, TLB invalidation, CP15 register accessors, interrupt priority routines, `setlabel`/`gotolabel`, `wfi`, `coherence`, `cas`, and `_tas`.
- Includes `cache.v7.s` for broader cache operations.

Integration:
- Supplies primitives used by `main.c`, `mmu.c`, `trap.c`, and locking code.
- Depends on constants and macros from `arm.s`/`mem.h`.

Risks/notes:
- Locking atomics depend on L1 cache/exclusive monitor state.
- Early mappings and cache/TLB order are hardware-sensitive; comments show empirical sequencing for Tegra 2/Cortex-A9.
