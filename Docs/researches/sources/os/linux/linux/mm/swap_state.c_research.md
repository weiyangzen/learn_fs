# File Research: sources/os/linux/linux/mm/swap_state.c

## Purpose
Implements the swap cache and swapin readahead. It maps swap entries to cached folios via per-cluster swap tables, manages swap-cache shadows for workingset refaults, prepares folios for swapin/zswap writeback, and provides cluster-based or VMA-based swap readahead.

## Main Interfaces
- Swap cache lookup: `swap_cache_get_folio()`, `swap_cache_has_folio()`, `swap_cache_get_shadow()`.
- Cache mutation: `__swap_cache_add_folio()`, `swap_cache_del_folio()`, `__swap_cache_del_folio()`, `__swap_cache_replace_folio()`.
- Free helpers: `free_swap_cache()`, `free_folio_and_swap_cache()`, `free_pages_and_swap_cache()`.
- Swapin allocation/read: `swap_cache_alloc_folio()`, `swapin_folio()`, `read_swap_cache_async()`.
- Readahead: `swap_update_readahead()`, `swap_cluster_readahead()`, `swapin_readahead()`.
- Sysfs: `mm/swap/vma_ra_enabled`.

## Control Flow
Swap-cache lookups read the per-cluster swap table under RCU and try to take a folio reference if the table entry encodes a PFN. Adding a folio validates the slots are present and not already cached, preserves any shadow, installs PFN entries, sets folio swapcache state, and accounts `NR_SWAPCACHE`.

Deleting a folio replaces PFN entries with shadow entries that preserve swap count, clears folio swapcache state, updates stats, and frees slots whose count is zero. Replacement updates PFN entries to point at a new folio while preserving counts.

Swapin first checks cache, verifies the slot is still swapped, allocates an order-0 folio under NUMA policy, charges memcg, adds it to swap cache, accounts memcg v1 swapin, handles workingset refault from a shadow, and starts swap I/O if it created the folio.

Readahead either reads a physical swap cluster based on `page_cluster` and recent hit counts, or scans neighboring PTEs in the faulting VMA and swaps in nearby entries. Readahead folios are marked with `PG_readahead` for later hit accounting.

## State And Synchronization
`swap_space` is a synthetic address space for swap cache writeback/reclaim paths. Swap cache entries are stored in `struct swap_table`, not the address-space XArray. Folio locks stabilize folio swap entries; cluster locks serialize table mutation; swap device references protect against swapoff.

## Dependencies
Uses swap table encoding, memcg swapin charging, workingset shadows, swap I/O plugs, NUMA mempolicy, fault VMA/PTE walking, shmem/migration address-space operations, and sysfs kobjects.

## Risks And Review Focus
- Large folio swapin intentionally falls back on races because aligned entries can conflict with smaller cached folios.
- Swap-cache deletion must preserve counts and free only truly unreferenced slots.
- VMA readahead walks lockless PTEs and must grab swap device refs for entries from non-target devices.
