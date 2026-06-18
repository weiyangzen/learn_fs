# File Research: sources/os/linux/linux/mm/sparse.c

## Purpose
Provides generic SPARSEMEM initialization. It records present physical memory sections, allocates `mem_section` roots for extreme sparsemem, allocates per-section usage metadata and memmap backing, initializes sections by NUMA node, and exposes sparsemem sizing helpers.

## Main Interfaces
- Global section storage: `mem_section`.
- Section index setup: `sparse_index_init()`.
- Section presence: `memory_present()`, `memblocks_present()`.
- Sizing helpers: `mem_section_usage_size()`, `section_map_size()`.
- Boot allocation buffer: `sparse_buffer_init()`, `sparse_buffer_alloc()`, `sparse_buffer_fini()`.
- Section init: `sparse_init_early_section()`, `sparse_init_nid()`, `sparse_init()`.

## Control Flow
Boot memory ranges are enumerated by `for_each_mem_pfn_range()` and rounded to section boundaries. Each present section gets an index initialized, a node id recorded, and early presence flags stored in `section_mem_map`.

`sparse_init()` groups contiguous present sections by early NUMA node id, initializes pageblock order, and calls `sparse_init_nid()` per node range. Per-node initialization allocates a contiguous usage buffer, prepares a memmap backing buffer aligned for the selected sparsemem mode, allows VMEMMAP preinit hooks, then populates and initializes each non-preinitialized section.

If allocation fails partway through a node range, later uninitialized present sections are cleared so unavailable memory is not exposed.

## State And Synchronization
Before real memmap installation, `section_mem_map` temporarily stores encoded NUMA node information. For `NODE_NOT_IN_PAGE_FLAGS`, `section_to_node_table` maps section numbers to node ids. `__highest_present_section_nr` tracks the highest present section so section iteration can stop early.

## Dependencies
Uses memblock, sparsemem section helpers, NUMA memory ranges, vmstat memmap accounting, VMEMMAP hooks from `sparse-vmemmap.c`, and boot-time pageblock setup.

## Risks And Review Focus
- `section_mem_map` has dual early/real meaning, so ordering of node-id clearing and section initialization matters.
- Allocation failure handling intentionally hides remaining sections; partial initialization must not leave invalid present sections.
- VMEMMAP and non-VMEMMAP modes have different memmap backing alignment requirements.
