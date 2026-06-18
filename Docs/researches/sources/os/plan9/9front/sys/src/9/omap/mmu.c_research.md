# File Research: sources/os/plan9/9front/sys/src/9/omap/mmu.c

ARMv7 MMU and page-table management for the OMAP kernel.

Key behavior:
- `mmuinit` initializes kernel L1 mappings for DRAM, I/O, vectors, and device mappings, then enables the MMU domain setup.
- `mmumap` installs section mappings; `mmuidmap` identity-maps physical memory windows.
- `mmuswitch` changes the current process address space and repopulates user L1 entries.
- `flushmmu` and `mmurelease` clear stale process mappings.
- `putmmu` allocates L2 page tables as needed, installs user page mappings, handles cacheability/write bits, and invalidates relevant TLB/cache state.
- `mmuuncache` converts a virtual range to uncached mappings.
- `mmukmap`/`mmukunmap` map and unmap physical ranges in a fixed segment map area.
- `cankaddr`, `vmap`, and `vunmap` provide physical-to-kernel mapping helpers.

Research notes:
- The implementation uses Plan 9 `Page` objects to back L2 page tables and keeps per-process `mmul2` lists.
- Cache/TLB maintenance is explicit around page-table updates.
