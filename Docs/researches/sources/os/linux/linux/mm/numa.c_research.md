# File Research: sources/os/linux/linux/mm/numa.c

## Role

Small generic NUMA initialization support file. It owns the exported `node_data[]` array, allocates per-node `pg_data_t` structures during early boot, and provides fallback node-lookup stubs when architecture-specific or `numa_memblks` implementations are not compiled in.

## Key Behavior

- Defines and exports `struct pglist_data *node_data[MAX_NUMNODES]`, the core per-node memory-management data pointer table used through `NODE_DATA(nid)`.
- `alloc_node_data()` allocates one cacheline-aligned `pg_data_t` via `memblock_phys_alloc_try_nid()`, preferring memory local to the target NUMA node. It panics on allocation failure because node data is mandatory during boot.
- Reports the physical range used for `NODE_DATA(nid)`, checks whether the actual allocation landed on a different node through `early_pfn_to_nid()`, stores the virtual address in `node_data[nid]`, and zeroes the structure.
- `alloc_offline_node_data()` allocates zeroed memory for an offline node's `pg_data_t` through `memblock_alloc_or_panic()`.
- If not supplied elsewhere, `memory_add_physaddr_to_nid()` and `phys_to_target_node()` warn once and return node 0 for memory-hotplug target-node queries.

## Dependencies

Uses early boot `memblock`, NUMA node APIs, physical-to-virtual conversion, printk, and declarations from `linux/numa.h` and `linux/numa_memblks.h`.

## Research Notes

This file is intentionally narrow. Architecture and memblock parsing code decide topology; this file provides the generic storage and allocation primitives that later memory-management code relies on. The fallback node stubs preserve functionality on platforms that do not keep address-to-node meminfo after boot, at the cost of less accurate hotplug placement.
