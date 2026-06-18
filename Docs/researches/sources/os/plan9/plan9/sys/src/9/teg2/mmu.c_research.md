# File Research: sources/os/plan9/plan9/sys/src/9/teg2/mmu.c

ARMv7 MMU management for kernel mappings, per-process user mappings, and per-CPU L1 tables.

Key behavior:
- Dumps and summarizes L1 page-table ranges for diagnostics.
- Maps MMIO sections, high vectors, AHB/NOR aliases, and private memory region attributes.
- Expands L1 section mappings into L2 page tables when page-granular control is needed.
- Allocates early L2 tables from high reserved memory.
- Maintains per-process L2 page-table pages and swaps them into the current CPU’s L1 table on `mmuswitch`.
- Implements `putmmu`, `flushmmu`, `mmurelease`, `mmuuncache`, `mmukmap`, `mmukunmap`, `vmap`, and `vunmap`.

Notes:
- Uses both L1 and L2 cache operations around page-table writes due to observed hardware behavior.
- User mappings are cleared broadly from `L1lo` to `L1hi`; a narrower optimization is disabled as buggy.
