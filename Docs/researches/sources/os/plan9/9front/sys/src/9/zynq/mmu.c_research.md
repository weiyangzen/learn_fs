# File Research: sources/os/plan9/9front/sys/src/9/zynq/mmu.c

Purpose: Zynq ARM MMU, mapping, and cache-address helper implementation.

Key behavior:
- `mmuinit` records current L1 table, installs per-CPU temp-map L2, and maps MPCORE/SLCR/OCM once.
- `l1switch`, `l1alloc/free`, and `upallocl1` manage per-process L1 tables and ASIDs.
- `l2free`, `mmuswitch`, `putmmu`, `flushmmu`, `mmurelease` manage user mappings and process MMU lifetime.
- `paddr`, `kaddr`, `cankaddr` convert between virtual and physical spaces for direct, VMAP, and OCM ranges.
- `kmap/kunmap` provide temporary per-process kernel mappings.
- `tmpmap/tmpunmap` provide per-CPU temporary mappings with interrupts high.
- `vmap` maps device MMIO as uncached/device/noexec.
- `ucalloc` allocates uncached memory from OCM for DMA descriptors/buffers.

Integration notes: Uses page allocator, process state, cache/TLB assembly helpers, `mpcore/slcr/ocm` globals, and Plan 9 VM conventions.

Risk/attention points: Temporary mappings panic if used at low interrupt priority. `ucalloc` is a simple downward allocator from OCM and does not free.
