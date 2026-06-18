# File Research: sources/os/linux/linux/mm/swap_table.h

## Purpose
Defines the per-cluster swap table format and helpers. The table is a 1:1 atomic entry array for slots in one `SWAPFILE_CLUSTER`, encoding free, shadow, cached folio PFN, reserved pointer marker, and bad-slot states with embedded swap counts.

## Main Interfaces
- Table type: `struct swap_table`.
- Encoders: `null_to_swp_tb()`, `pfn_to_swp_tb()`, `folio_to_swp_tb()`, `shadow_to_swp_tb()`.
- Type checks: `swp_tb_is_null()`, `swp_tb_is_folio()`, `swp_tb_is_shadow()`, `swp_tb_is_bad()`, `swp_tb_is_countable()`.
- Decoders: `swp_tb_to_folio()`, `swp_tb_to_shadow()`, `swp_tb_get_count()`.
- Locked table access: `__swap_table_set()`, `__swap_table_xchg()`, `__swap_table_get()`.
- RCU read access: `swap_table_get()`.

## Control Flow
A null entry is free. A shadow entry uses the XArray value encoding and carries a swap count plus optional workingset/memcg shadow value. A PFN entry points to the cached folio backing the slot and carries a swap count. A bad entry reserves unusable slots such as the swap header or holes.

Counts occupy high bits and can represent normal countable states up to `SWP_TB_COUNT_MAX`; overflow counts are stored externally in the cluster extension table owned by `swapfile.c`.

## State And Synchronization
The table pointer is RCU-protected through `swap_cluster_info->table`. Mutating helpers require the cluster lock. `swap_table_get()` safely reads through RCU and returns null if a cluster table is absent.

## Dependencies
Used by `swapfile.c` for allocation/count/free and by `swap_state.c` for cache lookup/mutation. Depends on folio PFN conversion, XArray value encoding, atomic longs, RCU, and cluster locking from `swap.h`.

## Risks And Review Focus
- Bit layout must fit PFN width plus marker bits plus count bits on every architecture.
- Shadow encoding relies on XArray value representation matching `SWP_TB_SHADOW_MARK`.
- Readers must verify the decoded folio is still refcountable and still matches the swap entry after locking.
