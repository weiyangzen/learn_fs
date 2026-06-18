# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_object.c

## Role

`dmu_object.c` implements DMU object allocation, claiming, reclaiming, freeing, iteration, spill removal, and zapification. It is the object-ID and dnode-allocation layer above dnode primitives.

## Major Responsibilities

- Allocates new DMU objects using per-CPU allocation cursors to reduce lock contention.
- Supports variable dnode sizes and indirect block size allocation variants.
- Claims specific object IDs during receive/import-style workflows.
- Reclaims existing objects by reallocating their dnodes.
- Removes spill blocks from objects.
- Frees objects and their ranges.
- Iterates allocated objects or holes.
- Converts MOS objects to extensible ZAP metadata format and handles feature accounting.

## Key Tunable

- `dmu_object_alloc_chunk_shift = 7`: each concurrent allocator grabs chunks of `2^shift` dnode slots, defaulting to 128 slots. The implementation clamps chunk size to at least one dnode block and at most one L1 dnode span.

## Important Functions

- `dmu_object_alloc_impl()` is the core allocator:
  - Normalizes requested dnode slots.
  - Uses a CPU-specific object cursor from `os_obj_next_percpu`.
  - Refills per-CPU chunks from `os_obj_next_chunk` under `os_obj_lock`.
  - Periodically searches for sparse dnode regions with `dnode_next_offset()`.
  - Preserves traversal expectations by using multiple dnode blocks before reusing older holes.
  - Holds candidate dnodes with `DNODE_MUST_BE_FREE`.
  - Allocates the dnode under `dn_struct_rwlock`, handles races, and records the new object in the transaction.
- `dmu_object_alloc()`, `dmu_object_alloc_ibs()`, and `dmu_object_alloc_dnsize()` are public wrappers for common allocation variants.
- `dmu_object_claim()` and `dmu_object_claim_dnsize()` allocate a specified free object ID.
- `dmu_object_reclaim()` and `dmu_object_reclaim_dnsize()` reinitialize an already allocated object, optionally preserving spill state.
- `dmu_object_rm_spill()` removes spill block state if present.
- `dmu_object_free()` frees all ranges and frees the dnode.
- `dmu_object_next()` finds the next allocated object or hole after a starting object, with special handling for large dnodes to scan the remaining current meta-dnode block before falling back to `dnode_next_offset()`.
- `dmu_object_zapify()` converts a syncing-context MOS object to `DMU_OTN_ZAP_METADATA`, initializes the microzap first, marks the dnode dirty, and increments `SPA_FEATURE_EXTENSIBLE_DATASET`.
- `dmu_object_free_zapified()` decrements the extensible dataset feature if needed, then frees the object.

## Interactions

- Uses meta-dnode geometry and `dnode_next_offset()` to find free or sparse dnode regions.
- Uses `dnode_hold_impl()` with allocation-state constraints.
- Uses `dnode_allocate()`, `dnode_reallocate()`, `dnode_free_range()`, `dnode_free()`, and `dnode_rm_spill()`.
- Uses transaction helpers such as `dmu_tx_add_new_object()`.
- Uses feature accounting for `SPA_FEATURE_EXTENSIBLE_DATASET`.
- Uses ZAP creation internals for zapification.

## Notable Invariants

- Object 0 is skipped by iteration/allocation convention; allocation starts from valid dnode object IDs.
- `DMU_META_DNODE_OBJECT` can only be claimed/freed in private transaction contexts where explicitly allowed.
- Large dnode allocation must account for multi-slot dnodes and avoid selecting middle slots.
- Allocation handles races where another thread claims a candidate between discovery and struct-lock acquisition.
- Zapification initializes ZAP contents before changing the object type so concurrent zapified checks do not observe a partially converted object.
- `dmu_object_free()` creates a full free range before freeing the dnode to avoid leaking indirect blocks during sync.

## Research Notes

This file is allocation-policy heavy rather than IO-heavy. The allocator balances per-CPU concurrency, sparse-region reuse, large-dnode slot correctness, and traversal assumptions. Changes here should be tested with large dnodes, object reuse after frees, receive/claim paths, and dmu traversal behavior.
