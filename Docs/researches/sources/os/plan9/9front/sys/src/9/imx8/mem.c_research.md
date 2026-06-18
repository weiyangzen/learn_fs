# File Research: sources/os/plan9/9front/sys/src/9/imx8/mem.c

Role: i.MX8 early page-table setup, physical memory discovery, kernel RAM mapping, and uncached allocation.

Key responsibilities:
- `mmuidmap()` builds initial TTBR0 identity blocks for VDRAM until physical `-KZERO`.
- `mmu0init()` builds shared TTBR1 kernel mappings for initial DRAM and VIRTIO device space, using blocks where aligned and pages for unaligned tail.
- Installs higher-level page-table links for configured `PTLEVELS`.
- `meminit()` defines three memory banks: kernel-after-end to `UCRAMBASE`, post-uncached area to 4 GiB, and 4 GiB to 5 GiB quad-A53 memory.
- Calls `kmapram()` for all memory ranges and computes per-bank page counts.
- `ucramalloc()` allocates descending aligned memory from the reserved uncached region and maps pages uncached when allocation crosses page boundaries.
- `ucalloc()` wraps `ucramalloc()` with 8-byte alignment and `PTEUNCACHED`.

Dependencies:
- Relies on `mem.h` address layout, `end`, `mmukmap`, `kmapram`, and page-table macros.

Notes:
- The reserved uncached region is excluded from normal memory in `meminit()`.
