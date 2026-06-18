# File Research: sources/os/linux/linux/mm/numa_memblks.c

## Role

Generic early-boot NUMA memory-block parser and registrar. It collects firmware/architecture-provided memory ranges per node, sanitizes and merges them, registers node ownership in memblock, handles NUMA distances, preserves reserved-range node metadata when configured, and supplies physical-address-to-node helpers for memory hotplug.

## Key Behavior

- Maintains `numa_nodes_parsed`, `numa_meminfo`, optional `numa_reserved_meminfo`, `numa_distance_cnt`, and the dynamically allocated `numa_distance` table.
- `numa_reset_distance()` frees the current memblock-allocated distance table and resets the allocation sentinel. `numa_alloc_distance()` sizes the table from parsed nodes and memory blocks, allocates it from memblock, and initializes local and remote defaults.
- `numa_set_distance()` lazily allocates the distance table, validates node bounds and distance values, and records one directional distance. Invalid calls warn once and are ignored. `__node_distance()` returns stored distances or local/remote defaults.
- `numa_add_memblk()` and `numa_add_reserved_memblk()` append validated ranges into regular or reserved meminfo. Zero-length ranges are ignored, invalid node/range inputs warn, and `NR_NODE_MEMBLKS` overflow fails.
- `numa_cleanup_meminfo()` trims regular blocks to actual DRAM, moves non-DRAM or above-DRAM pieces to reserved meminfo, removes empty blocks, detects overlapping ranges from different nodes as fatal, warns and merges overlaps from the same node, and merges same-node neighbors when gaps are not covered by another node.
- `numa_clear_kernel_node_hotplug()` marks nodes containing kernel-reserved memory as not hotpluggable. It first assigns node ids to reserved memblock regions by splitting along parsed node blocks, then clears `MEMBLOCK_HOTPLUG` on all blocks belonging to nodes that contain reserved memory.
- `numa_register_meminfo()` builds `node_possible_map` from parsed CPU nodes and memory nodes, writes node ids into `memblock.memory`, clears kernel-node hotplug state, and validates PFN-to-node granularity when `NODE_NOT_IN_PAGE_FLAGS` requires section alignment.
- `numa_memblks_init()` is the main init wrapper. It clears node maps and meminfo, resets all memblock node ids and hotplug flags, resets distances, runs an architecture-provided parser, restores top-down memblock allocation if requested, cleans meminfo, optionally applies NUMA emulation, and registers the final meminfo.
- `numa_fill_memblks()` finds existing memblocks overlapping a requested physical range, sorts pointers by start address, expands first and last blocks to cover the ends, and adjusts following starts to fill holes between overlapping blocks. It returns `NUMA_NO_MEMBLK` when no blocks overlap.
- Under `CONFIG_NUMA_KEEP_MEMINFO`, `phys_to_target_node()` and `memory_add_physaddr_to_nid()` use retained meminfo to map physical addresses to target or online node ids, preferring reserved metadata when relevant.

## Dependencies

Uses memblock memory and reserved region APIs, node masks, sorting, printk, architecture NUMA definitions, optional NUMA emulation, hotplug flags, PFN section alignment helpers, and exported node-distance consumers.

## Research Notes

This file is the bridge from firmware/architecture topology parsing to generic Linux memory-management topology. It is intentionally strict about cross-node overlaps because those corrupt PFN-to-node ownership. It also preserves enough reserved-address metadata to make later memory hotplug placement more accurate when `CONFIG_NUMA_KEEP_MEMINFO` is enabled.
