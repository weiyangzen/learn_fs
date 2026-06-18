# File Research: sources/os/plan9/plan9/sys/src/9/omap/mmu.c

ARMv7 OMAP MMU management for kernel mappings, user page tables, TLB switching, and simple kernel mappings.

Key responsibilities:
- Dumps level-1 page-table ranges through `mmudump`.
- Adds section mappings with `mmumap` and identity mappings with `mmuidmap`.
- `mmuinit` completes static kernel mappings for I/O and high vectors, including a 4 KiB vector L2 table.
- Maintains per-process user L2 page-table pages in `Proc.mmul2` and `Proc.mmul2cache`.
- Switches process address spaces in `mmuswitch`, flushes stale mappings, and writes back page-table entries.
- Releases process MMU pages in `mmurelease`.
- Installs user mappings in `putmmu`.
- Provides section-level `mmuuncache`, `mmukmap`, `mmukunmap`, `cankaddr`, `vmap`, and `vunmap`.

Important behavior:
- User virtual space covered by `L1lo` through `L1hi` is cleared on switches.
- Allocates full pages for L2 tables even though each coarse ARM L2 table needs only 1 KiB.
- `putmmu` maps pages cached/buffered unless `PTEUNCACHED` is set, uses user RW or RO access bits, invalidates the specific TLB entry, and handles text-cache invalidation.
- `mmuuncache` only accepts already mapped 1 MiB sections.
- `mmukmap`/`mmukunmap` are section-size stubs.

Dependencies:
- Uses `ttbget`, cache/TLB assembly helpers, page allocator, process fields from `dat.h`, and ARM PTE constants from `arm.h`.

Notable risks:
- `mmul1empty` contains a disabled optimized path with a comment noting a bug; current code clears the entire user L1 range.
- `vmap` is a transitional implementation and comments call out multiple limitations.
- `mmukmap` asserts 1 MiB alignment and size, so sub-MiB users will fail.
