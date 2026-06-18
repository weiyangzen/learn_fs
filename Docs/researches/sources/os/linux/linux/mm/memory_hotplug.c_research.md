# File Research: sources/os/linux/linux/mm/memory_hotplug.c

## Purpose

Implements Linux memory hotplug and hotremove plumbing for adding physical memory ranges, creating memory block devices, onlining/offlining pages, updating zones/nodes, and removing memory again. It coordinates architecture memory map operations, sparsemem section management, sysfs memory blocks, firmware maps, node state transitions, and allocator-visible page state.

## Core State and Policy

Key global state includes:

- `mem_hotplug_lock`, a percpu rwsem protecting memory online/offline transitions.
- `online_page_callback`, normally `generic_online_page()`, allowing special page onlining behavior.
- `memmap_mode`, controlled by `memory_hotplug.memmap_on_memory`.
- `online_policy`, controlled by `memory_hotplug.online_policy`.
- `auto_movable_ratio` and `auto_movable_numa_aware`, used by automatic ZONE_MOVABLE placement.
- `movable_node_enabled`, set by the `movable_node` boot parameter.
- `mhp_default_online_type`, set by Kconfig defaults or `memhp_default_state=`.

The file enforces memory-block alignment for public hotplug paths and subsection alignment for lower-level add/remove page paths.

## Add and Online Flow

The primary external add paths are:

- `add_memory()`
- `__add_memory()`
- `add_memory_driver_managed()`
- `add_memory_resource()`

`register_memory_resource()` reserves the physical address range under `iomem_resource`, rejects ranges outside `mhp_get_pluggable_range()`, and marks driver-managed System RAM specially.

`add_memory_resource()` performs the main sequence:

1. Validate block alignment and resolve memory groups.
2. Acquire `mem_hotplug_lock` through `mem_hotplug_begin()`.
3. Optionally update retained memblock metadata.
4. Initialize/register a previously offline NUMA node if needed.
5. Add memory through `arch_add_memory()` or per-block altmaps for memmap-on-memory.
6. Create memory block devices.
7. Register memory blocks under the node and firmware hotplug map.
8. Release the hotplug lock.
9. Merge resources if requested.
10. Auto-online memory blocks if the default online type is not offline.

`__add_pages()` is the lower-level sparsemem section population helper used by architectures and device memory paths.

## Zone Selection

`zone_for_pfn_range()` chooses where memory should be onlined:

- `MMOP_ONLINE_KERNEL` chooses a kernel zone, preferring an intersecting low/normal zone and otherwise ZONE_NORMAL.
- `MMOP_ONLINE_MOVABLE` chooses ZONE_MOVABLE.
- `MMOP_ONLINE` follows `online_policy`.
- `contig-zones` inherits an existing non-overlapping zone when possible.
- `auto-movable` uses MOVABLE:KERNEL_EARLY ratios and memory group state to decide whether the range can safely become ZONE_MOVABLE.

The auto-movable logic treats CMA pages as movable, tracks dynamic memory groups separately, and optionally applies NUMA-local ratio checks.

## Page and Zone State Mutation

Important helpers:

- `move_pfn_range_to_zone()` associates a PFN range with a zone, resizes zone/pgdat spans, initializes memmap entries, sets migratetypes, and handles ZONE_DEVICE subsection taint.
- `remove_pfn_range_from_zone()` poisons struct pages, shrinks zone spans when possible, updates pgdat span, and restores zone contiguity metadata.
- `adjust_present_page_count()` updates zone, node, early-present, and memory-group counters.
- `online_pages_range()` frees hotplugged pages via `online_page_callback` and marks sections online.

`online_pages()` performs notifier calls, zone setup, isolated pageblock accounting, section onlining, present-page accounting, zonelist rebuilds, pageblock un-isolation, page shuffling, watermark recalculation, kswapd/kcompactd startup, and final `MEM_ONLINE` notification.

## Memmap-on-Memory

When `CONFIG_MHP_MEMMAP_ON_MEMORY` is enabled, vmemmap pages can be allocated from the hotplugged memory itself.

Relevant functions:

- `mhp_supports_memmap_on_memory()`
- `mhp_init_memmap_on_memory()`
- `mhp_deinit_memmap_on_memory()`
- `create_altmaps_and_memory_blocks()`
- `remove_memory_blocks_and_altmaps()`

The feature requires pageblock-compatible vmemmap sizing and architecture support. Forced mode can pad vmemmap pages to pageblock alignment, wasting pages in each memory block.

## Hotremove and Offline Flow

Under `CONFIG_MEMORY_HOTREMOVE`, `offline_pages()` is the central offlining operation. It:

1. Verifies alignment and absence of memory holes.
2. Disables PCP lists and LRU cache.
3. Isolates the page range.
4. Sends node and memory notifiers.
5. Repeatedly scans for movable pages with `scan_movable_pages()`.
6. Migrates movable folios with `do_migrate_range()`.
7. Dissolves free hugetlb folios.
8. Confirms isolation.
9. Removes isolated free pages from the buddy allocator.
10. Updates managed/present counters and node states.
11. Rebuilds zonelists and stops per-node daemons if the node becomes memoryless.
12. Sends `MEM_OFFLINE` and removes the PFN range from the zone.

Removal APIs include:

- `remove_memory()`
- `__remove_memory()`
- `offline_and_remove_memory()`
- `try_offline_node()`

`try_remove_memory()` requires all memory blocks offline, removes firmware map entries, removes memory block devices, calls `arch_remove_memory()`, updates retained memblock metadata, releases the resource, and may unregister the NUMA node.

`offline_and_remove_memory()` records per-block online types, attempts to offline all blocks, removes memory, and re-onlines previously offlined blocks on failure.

## Locking and Notifications

- `device_hotplug_lock` serializes external hotplug and sysfs online/offline operations.
- `mem_hotplug_lock` protects core memory topology changes.
- CPU hotplug read locking is acquired while holding the hotplug write side.
- `online_page_callback_lock` protects callback replacement.
- Zone locks protect isolated pageblock counters.
- Node and memory notifier chains gate transitions such as first memory added and last memory removed.

## Integration Points

This file integrates with sparsemem, memblock, `/proc/iomem`, firmware memory maps, sysfs memory blocks, NUMA node registration, page migration, hugetlb, compaction, writeback ratelimits, KASAN shadow setup, memory groups, ZONE_DEVICE, and architecture-specific add/remove memory hooks.

## Risks and Invariants

The key invariants are alignment, section/block granularity, single-zone offlining ranges, all-blocks-offline removal, consistent zone/node span accounting, and correct notifier rollback. Offlining is sensitive to unmovable pages, migration races, hugetlb state, memory holes, and concurrent sysfs operations. Memmap-on-memory adds extra risk because altmap accounting must fully unwind and vmemmap self-hosted pages must be marked online/offline consistently.
