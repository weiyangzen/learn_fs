# File Research: sources/os/plan9/9front/sys/src/9/kw/mmu.c

Kirkwood ARM MMU management. It builds/refines vector and MMIO mappings, manages process L1/L2 page-table state, switches address spaces, installs user PTEs, and exposes simple kernel mapping helpers.

`mmuinit` maps high vectors and virtual zero through L2 tables to physical DRAM, replaces the broad MMIO section with small-page mappings, optionally exposes crypto sandbox pages, and stores the L1 pointer in `m->mmul1`.

Per-process mappings use coarse L1 entries pointing to small-page L2 tables stored in `Proc.mmul2`. `mmuswitch`, `flushmmu`, `mmurelease`, and `putmmu` maintain L1 entries, write back caches, invalidate TLBs, and flush I-cache for text changes.

`mmuuncache`, `mmukmap`, `mmukunmap`, `cankaddr`, `vmap`, and `vunmap` provide limited section-based helpers for uncached memory and physical mapping.

Notable risks: comments identify wasteful 4 KiB allocation for 1 KiB L2 tables, a disabled buggy optimization in `mmul1empty`, and temporary/crocked `vmap` behavior.
