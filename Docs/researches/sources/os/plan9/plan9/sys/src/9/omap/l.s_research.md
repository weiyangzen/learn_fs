# File Research: sources/os/plan9/plan9/sys/src/9/omap/l.s

ARMv7/OMAP3530 assembly assist for kernel entry, MMU/cache setup, reset, cache maintenance, interrupt priority primitives, atomic operations, labels, and CP15 accessors.

Key responsibilities:
- `_start` enters from U-Boot or another kernel with MMU disabled, sets SVC mode, prints early boot characters, applies Cortex/OMAP errata workarounds, clears `Mach`, builds first-level page tables, maps DRAM and MMIO, enables caches and MMU, then jumps into virtual-addressed C `main`.
- `_reset` disables caches, re-establishes temporary mappings, disables the MMU, and attempts a low-level reset path.
- Provides cache line operations: `cachedwbse`, `cachedwbinvse`, `cachedinvse`, plus full cache helpers via `cache.v7.s`.
- Provides MMU helpers: `mmuenable`, `mmudisable`, `mmuinvalidate`, `mmuinvalidateaddr`, `ttbget`, `ttbput`, `dacget`, `dacput`, `pidput`, `pidget`.
- Provides CP15/status helpers: CPU ID, cache type, control register, fault status/address, SCR.
- Implements `splhi`, `spllo`, `splx`, `islo`, `tas`, `clz`, `setlabel`, `gotolabel`, `getcallerpc`, `idlehands`, and `coherence`.

Important behavior:
- Sets up a double map for early physical and kernel virtual DRAM, then removes the physical alias after entering the virtual map.
- Maps up to 512 MiB of DRAM at `KZERO`, matching Beagle/IGEP comments.
- Uses high exception vectors later populated by `trapinit`.
- Uses `SWPW` for test-and-set even though it is deprecated on ARMv7.
- Uses barriers aggressively around CP15, MMU, cache, and interrupt state changes.

Dependencies:
- Depends on constants/macros from `arm.s`, `mem.h`, and MMU page-table macros such as `FILLPTE`, `ZEROPTE`, `PTEDRAM`, and `PTEIO`.
- Calls C/assembly routines including `cachedinv`, `cacheuwbinv`, `l2cacheuwbinv`, `main`, and `_div`.

Notable risks:
- Early startup has no normal stack until it creates one, so only very constrained calls are safe before that point.
- Low-level mapping mistakes can hang CP15/TLB operations.
- Reset path is incomplete for actual flash vector jump and falls into idle loop.
