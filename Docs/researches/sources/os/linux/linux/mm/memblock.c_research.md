# File Research: sources/os/linux/linux/mm/memblock.c

## Purpose

Implements Linux `memblock`, the early-boot physical memory region allocator and map manager used before the normal slab and buddy allocators are ready. It tracks usable memory, reserved allocations, and optionally the physical memory map through sorted region arrays.

This file owns the lifecycle from firmware-discovered physical ranges, through early boot reservations and allocations, to final release of free pages into the buddy allocator.

## Core State

The global `memblock` object contains:

- `memblock.memory`: usable physical memory ranges.
- `memblock.reserved`: allocated or otherwise reserved ranges.
- `memblock.current_limit`: upper bound for accessible early allocations.
- `memblock.bottom_up`: allocation direction policy.

Optional state includes:

- `physmem` under `CONFIG_HAVE_MEMBLOCK_PHYS_MAP`.
- `kho_scratch_only` under `CONFIG_MEMBLOCK_KHO_SCRATCH`.
- `system_has_some_mirror` for mirrored-memory preference.
- `memblock_can_resize`, plus slab-origin flags for dynamically grown region arrays.
- `memblock_memory`, a retained pointer used by iterators and nulled by `memblock_discard()` when memblock is not kept after init.

Initial static region arrays are sized by `INIT_MEMBLOCK_MEMORY_REGIONS`, `INIT_MEMBLOCK_RESERVED_REGIONS`, and `INIT_PHYSMEM_REGIONS`.

## Region Model

Each `struct memblock_region` has a base, size, flags, and NUMA node id. The region arrays are maintained as sorted, non-overlapping, minimal ranges where neighboring compatible entries are merged.

Important internal operations:

- `memblock_cap_size()` prevents physical address overflow.
- `memblock_add_range()` adds a possibly overlapping range using a two-pass algorithm: first count needed splits, then insert and merge.
- `memblock_isolate_range()` splits boundary-crossing regions so a target interval can be modified exactly.
- `memblock_remove_range()` isolates and removes a range.
- `memblock_merge_regions()` coalesces adjacent regions with matching node and flags.
- `memblock_double_array()` grows region arrays, using slab if available or memblock allocation otherwise, and reserves the new backing storage when needed.

The file uses `BUG_ON()` and `WARN_ON()` heavily to enforce invariants such as sorted ordering, compatible merge boundaries, and array capacity.

## Public Memory Map APIs

The main map mutation APIs are:

- `memblock_add_node()`: add memory with an explicit NUMA node.
- `memblock_add()`: add memory without a NUMA node.
- `memblock_remove()`: remove memory from the memory map.
- `__memblock_reserve()`: add a reserved range with node and flags.
- `memblock_physmem_add()`: add to optional `physmem`.
- `memblock_set_node()`: assign NUMA node ids to isolated ranges.

Query APIs include:

- `memblock_is_reserved()`
- `memblock_is_memory()`
- `memblock_is_map_memory()`
- `memblock_is_region_memory()`
- `memblock_is_region_reserved()`
- `memblock_search_pfn_nid()`
- `memblock_start_of_DRAM()`
- `memblock_end_of_DRAM()`
- `memblock_phys_mem_size()`
- `memblock_reserved_size()`
- `memblock_reserved_kern_size()`
- `memblock_estimated_nr_free_pages()`

## Allocation Flow

Allocation is based on intersections between `memory` and the inverse of `reserved`.

Key functions:

- `__memblock_find_range_bottom_up()`
- `__memblock_find_range_top_down()`
- `memblock_find_in_range_node()`
- `memblock_alloc_range_nid()`
- `memblock_phys_alloc_range()`
- `memblock_phys_alloc_try_nid()`
- `memblock_alloc_internal()`
- `memblock_alloc_exact_nid_raw()`
- `memblock_alloc_try_nid_raw()`
- `memblock_alloc_try_nid()`
- `__memblock_alloc_or_panic()`

`memblock_alloc_range_nid()` is the central allocator. It chooses memory flags, finds a suitable free range, reserves it as `MEMBLOCK_RSRV_KERN`, records kmemleak metadata unless disabled with `MEMBLOCK_ALLOC_NOLEAKTRACE`, and calls `accept_memory()` for platforms that require guest memory acceptance.

Fallback behavior includes:

- retrying non-exact NUMA allocations on any node;
- retrying mirrored allocations on non-mirrored memory with a ratelimited warning;
- falling back below `min_addr` in the virtual-address allocation helpers;
- using `kzalloc_node()` if a memblock allocation API is accidentally called after slab availability.

## Flags and Filtering

The file manages memory and reserved flags through `memblock_setclr_flag()` after isolating the affected range.

Memory flags handled here include:

- `MEMBLOCK_HOTPLUG`
- `MEMBLOCK_MIRROR`
- `MEMBLOCK_NOMAP`
- `MEMBLOCK_DRIVER_MANAGED`
- `MEMBLOCK_KHO_SCRATCH`

Reserved flags handled here include:

- `MEMBLOCK_RSRV_NOINIT`
- `MEMBLOCK_RSRV_KERN`

`should_skip_region()` centralizes iterator filtering. It skips regions based on NUMA node, movable-node hotplug behavior, mirror-only allocation, `NOMAP`, driver-managed memory, and KHO scratch-only allocation mode.

## Iterators

This file implements the generic range iteration backends used by memblock macros:

- `__next_mem_range()`: forward iteration over `type_a` excluding `type_b`.
- `__next_mem_range_rev()`: reverse iteration.
- `__next_mem_pfn_range()`: PFN range iteration for memory regions.

The iterator index packs two 32-bit cursors into a `u64`, allowing lockstep traversal of sorted included and excluded region arrays.

## Memory Limits and Trimming

Boot parameters and architecture setup can restrict available memory through:

- `memblock_enforce_memory_limit()`
- `memblock_cap_memory_range()`
- `memblock_mem_limit_remove_map()`
- `memblock_trim_memory()`
- `memblock_set_current_limit()`
- `memblock_get_current_limit()`

`__find_max_addr()` translates a byte limit over discontiguous memory ranges into a physical cutoff address.

## Reserved Memory Freeing

`free_reserved_area()` converts virtual addresses to physical addresses, optionally removes the range from `memblock.reserved` when memblock is kept, poisons pages when requested, and returns pages through `free_reserved_page()`.

`memblock_free()` and `memblock_phys_free()` release previous memblock allocations. If slab is available, physical free also releases pages to the buddy allocator via `__free_reserved_area()`.

## Transition to Buddy Allocator

`memblock_free_all()` performs the final early-memory handoff:

1. `free_unused_memmap()` releases unused portions of the `mem_map` array on applicable memory models.
2. `reset_all_zones_managed_pages()` clears zone managed page counters once.
3. `memblock_clear_kho_scratch_only()` disables scratch-only allocation mode.
4. `free_low_memory_core_early()` initializes reserved page metadata and frees non-reserved memory ranges.
5. `totalram_pages_add()` adds freed pages to global RAM accounting.

Reserved page initialization is handled by:

- `memmap_init_reserved_range()`
- `memmap_init_reserved_pages()`

These functions mark reserved and `NOMAP` pages as `PageReserved` and initialize deferred pages as needed.

## Named reserve_mem Support

The `reserve_mem=` setup parameter parses `reserve_mem=<size>:<align>:<name>` and allocates a named memblock reservation.

State is stored in a fixed `reserved_mem_table` with up to eight entries. Exported/runtime APIs include:

- `reserve_mem_find_by_name()`
- `reserve_mem_release_by_name()`

Access is protected by `reserve_mem_lock`.

Under `CONFIG_KEXEC_HANDOVER`, named reservations can be preserved and revived across kexec handover using an FDT subtree:

- `prepare_kho_fdt()`
- `reserved_mem_preserve()`
- `reserve_mem_kho_retrieve_fdt()`
- `reserve_mem_kho_revive()`
- `reserve_mem_init()`

## Debugging Interfaces

Boot-time debug is enabled by `memblock=debug` through `early_param()`.

Debug output includes:

- `memblock_dump()`
- `__memblock_dump_all()`
- `memblock_dump_all()`

Under `CONFIG_DEBUG_FS`, `memblock_init_debugfs()` creates `debugfs` entries for memblock arrays when `CONFIG_ARCH_KEEP_MEMBLOCK` is enabled and for named `reserve_mem` entries when present.

## Integration Points

This file integrates with:

- architecture boot memory discovery and NUMA setup;
- kmemleak physical allocation tracking;
- KASAN tag reset during reserved-area poisoning;
- deferred struct page initialization;
- memory hotplug and movable-node policy;
- kexec handover preservation;
- debugfs reporting;
- the buddy allocator handoff path.

## Implementation Notes and Risks

The most important invariant is that region arrays remain sorted, non-overlapping, and merge-minimal. Allocation, reservation, flag mutation, NUMA assignment, and removal all depend on that property.

Most operations run during early boot and are not generally protected by global locks. The named reservation lookup/release path is an exception and uses a mutex because it can be queried after init.

Array resizing before all reserved ranges are known is dangerous; the file explicitly panics if resizing is attempted before `memblock_allow_resize()`.

`memblock_discard()` frees dynamic arrays and clears `memblock_memory` on configurations that do not keep memblock after init, so later code must not rely on discarded memblock metadata unless `CONFIG_ARCH_KEEP_MEMBLOCK` is enabled.
