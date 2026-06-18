# File Research: sources/os/linux/linux/mm/mm_init.c

## Role

`mm_init.c` coordinates early and late MM subsystem initialization. It verifies memory-init layout, parses memory-zone boot parameters, constructs zones/nodes, initializes `struct page` arrays, supports deferred struct-page initialization, initializes ZONE_DEVICE metadata, configures debug/hardening static keys, reports memory layout, and runs the main allocator/MM bootstrap sequence.

## Main Responsibilities

- Define global memory symbols such as `high_memory`, `zero_page_pfn`, and non-NUMA `mem_map`/`max_mapnr`.
- Create `/sys/kernel/mm`.
- Parse `kernelcore=`, `movablecore=`, `mminit_loglevel=`, `hashdist=`, `init_on_alloc=`, `init_on_free=`, and `check_pages=`.
- Determine zone PFN bounds, movable-zone placement, absent pages, and per-node totals.
- Initialize pgdat, zone internals, free lists, pageblock migratetypes, and flatmem memmaps.
- Initialize unavailable ranges as reserved pages so holes have safe `struct page` state.
- Initialize ZONE_DEVICE pages and compound device-page metadata.
- Defer initialization of high memory ranges when configured, then complete it in parallel later.
- Allocate large system hash tables during boot.
- Enable memory debugging/hardening static branches.
- Run `mm_core_init_early()`, `mm_core_init()`, and `page_alloc_init_late()` bootstrap phases.

## Zone and Node Initialization

`free_area_init()` obtains architecture zone limits, initializes sparsemem, computes possible zone ranges, finds per-node ZONE_MOVABLE start PFNs, prints early memory ranges, initializes node IDs and pageblock order, then calls `free_area_init_node()` for each node. `free_area_init_node()` computes a node PFN range, calculates zone totals, allocates flatmem node maps when needed, configures deferred ranges, initializes zone internals, and initializes LRU-generation pgdat state.

`find_zone_movable_pfns_for_nodes()` is the main policy routine for ZONE_MOVABLE placement. It handles `movable_node`, `kernelcore=mirror`, percentage and absolute `kernelcore`/`movablecore`, even distribution of kernelcore across usable nodes, and MAX_ORDER alignment.

`calculate_node_totalpages()` computes spanned and present pages per zone using `zone_spanned_pages_in_node()` and `zone_absent_pages_in_node()`, with special mirrored-memory handling where mirrored/unmirrored pages are treated as absent from the opposite zone.

## Struct Page Initialization

`__init_single_page()` zeroes and initializes a `struct page`, sets zone/node/pfn links, initializes refcount/mapcount/cpupid/KASAN tag/list state, and optionally sets direct virtual address metadata. `memmap_init_range()` initializes a PFN range for early boot, hotplug, or ZONE_DEVICE contexts, sets offline/reserved state where appropriate, initializes pageblock migratetype, and supports vmem altmap reservations.

`memmap_init()` walks memblock ranges by node and zone, initializes valid memory ranges, and explicitly initializes holes/trailing sections via `init_unavailable_range()` as reserved pages. This prevents later `struct page` users from observing uninitialized metadata for PFNs inside memmap coverage but outside actual RAM.

## Deferred Initialization

When `CONFIG_DEFERRED_STRUCT_PAGE_INIT` is enabled, high-zone struct-page initialization can stop after an initial section. `defer_init()` records `pgdat->first_deferred_pfn`; `deferred_grow_zone()` can initialize/free section-sized chunks on demand during early allocation; `page_alloc_init_late()` starts per-node `deferred_init_memmap` kernel threads and waits for completion. Deferred chunks initialize pages and free them to the buddy allocator, using larger naturally aligned frees when possible.

## ZONE_DEVICE Support

`memmap_init_zone_device()` initializes device memory pages after hotplug section activation. It handles altmap offsets, pgmap back-pointers, reserved state, pageblock migratetype, device-specific refcount initialization, and compound-page metadata when `pgmap->vmemmap_shift` groups PFNs. Supported pgmap types include FS DAX, private, coherent, PCI P2PDMA, and generic device memory.

## Boot Phases

- `mm_core_init_early()` reserves hugetlb CMA/bootmem and initializes zones via `free_area_init()`.
- `mm_core_init()` performs architecture preinit, zero-page setup, zonelist construction, CPU hotplug allocator setup, allocation tags, page-ext flatmem setup, debugging/hardening setup, KFENCE metadata allocation, meminit reporting, KMSAN setup, stack depot setup, KHO memory init, memblock release to buddy, slab initialization, kmemleak/page-table/vmalloc/debug-object setup, espfix/PTI, runtime KMSAN, MM cache init, and executable memory init.
- `page_alloc_init_late()` completes deferred page init, initializes buffer heads, discards memblock metadata, shuffles free memory, marks contiguous zones, initializes page extensions if deferred, and installs page-allocation sysctls.

## Debugging and Hardening

`mem_debugging_and_hardening_init()` coordinates page poisoning, debug pagealloc, guard pages, init-on-alloc, init-on-free, and page sanity checking static branches. Page poisoning takes precedence over heap auto-initialization. `report_meminit()` reports stack and heap initialization state; `mem_init_print_info()` prints available/reserved/CMA/highmem and kernel section sizes after accounting stabilizes.

## Utility Exports

`get_pfn_range_for_nid()`, `absent_pages_in_range()`, `node_map_pfn_alignment()`, `set_zone_contiguous()`, `pfn_range_intersects_zones()`, `memmap_alloc()`, `alloc_large_system_hash()`, and `memblock_free_pages()` are reusable helpers for architecture, hotplug, allocator, and subsystem initialization code.
