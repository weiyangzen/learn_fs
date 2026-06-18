# File Research: sources/os/plan9/9front/sys/src/9/bcm/mmu.c

32-bit ARM MMU setup and per-process user mapping management for BCM.

Key responsibilities:
- Initializes kernel L1/L2 mappings for DRAM, I/O, vectors, framebuffer, and device memory.
- Manages per-process L1 entries and L2 page-table allocation/release.
- Switches address spaces in `mmuswitch()` and flushes stale mappings.
- Installs user mappings through `putmmu()`.
- Handles cacheability changes with `mmuuncache()`.
- Provides physical-to-kernel mapping helpers: `cankaddr()`, `mmukmap()`, `kunmap()`, and `checkmmu()`.

Important behavior:
- Uses SoC-specific L1/L2 DRAM attributes from `soc`.
- Flushes TLB/cache state around page-table changes.
- Reuses Plan 9 `Page` refcounting for L2 page-table pages.

Dependencies:
- ARM page-table definitions, cache/TLB assembly helpers, `Proc`/`PMMU`, physical memory layout, and SoC configuration.
