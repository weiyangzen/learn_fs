# File Research: sources/os/linux/linux/mm/swap.h

## Purpose
Internal MM swap header defining swap cluster metadata, cluster flags, locking helpers, swap cache APIs, swap I/O hooks, readahead APIs, and no-op stubs for non-`CONFIG_SWAP` builds.

## Main Interfaces
- Cluster structure: `struct swap_cluster_info`.
- Cluster flags: `CLUSTER_FLAG_FREE`, `NONFULL`, `FRAG`, `FULL`, `DISCARD`.
- Lookup helpers: `__swap_type_to_info()`, `__swap_entry_to_info()`, `__swap_offset_to_cluster()`.
- Locking helpers: `swap_cluster_lock()`, `swap_cluster_get_and_lock()`, IRQ variants, unlock variants.
- Swap slot APIs: `folio_alloc_swap()`, `folio_dup_swap()`, `folio_put_swap()`.
- Swap cache APIs: `swap_cache_get_folio()`, `swap_cache_has_folio()`, `swap_cache_get_shadow()`, `swap_cache_del_folio()`, `__swap_cache_add_folio()`, `__swap_cache_replace_folio()`.
- Swap I/O and readahead: `swap_read_folio()`, `swap_writeout()`, `swap_cluster_readahead()`, `swapin_readahead()`, `swapin_folio()`.

## Control Flow
The header codifies the core synchronization contract: callers must validate entries and stabilize the swap device by holding a swap device reference, holding a locked swap-cache folio, or holding another lock protecting a swap entry such as a page-table lock.

Cluster locks protect cluster metadata and corresponding swap table entries. Locked swap-cache folios pin their swap slots, and folio-level swap APIs require locked folios to prevent entries from changing while counts or cache state are updated.

## State And Synchronization
`struct swap_cluster_info` owns a spinlock, slot count, cluster order, list flag, RCU-protected swap table pointer, optional overflow count table, and list linkage. Helpers warn on races with swapoff via `percpu_ref_is_zero(&si->users)`.

## Dependencies
Used by `swapfile.c`, `swap_state.c`, `page_io.c`, reclaim, fault, and migration code. Depends on `swapops`, folios, mempolicy, block I/O, and the per-cluster swap table declared in `swap_table.h`.

## Risks And Review Focus
- The documented stabilization rules are critical; using swap cache helpers without a device ref or equivalent lock can race with swapoff.
- Large folios must stay within one cluster for `swap_cluster_get_and_lock()` assumptions.
- Non-`CONFIG_SWAP` stubs intentionally return inert values and must match caller expectations.
