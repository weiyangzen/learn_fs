# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/bpobj.c

## Scope

Implements persistent ZFS block-pointer objects, used to store block pointers and nested block-pointer subobjects with space accounting for deferred frees, deadlists, and related pool metadata.

Read completely: 617 lines.

## Main APIs

Allocation and lifetime:

- `bpobj_alloc_empty()` returns the pool-wide empty bpobj when the feature is enabled, creating and feature-activating it as needed.
- `bpobj_decr_empty()` decrements the empty-bpobj feature and frees the shared empty object when no longer active.
- `bpobj_alloc()` allocates a DMU object with bonus size based on pool version.
- `bpobj_free()` recursively frees subobjects, then frees the bpobj object.
- `bpobj_open()` validates object type and bonus type, holds the bonus buffer, initializes lock/state, and records feature-derived capabilities.
- `bpobj_close()` releases held buffers and destroys the lock.
- `bpobj_is_open()` and `bpobj_is_empty()` expose state checks.

Iteration:

- `bpobj_iterate()` iterates and removes entries.
- `bpobj_iterate_nofree()` iterates without removal.
- `bpobj_iterate_impl()` handles both modes and recursively descends subobjects.

Mutation:

- `bpobj_enqueue()` appends a block pointer and updates byte/compressed/uncompressed accounting.
- `bpobj_enqueue_subobj()` appends another bpobj as a subobject, drops empty subobjects, and may flatten one-block nested subobject arrays.

Accounting:

- `bpobj_space()` returns stored accounting when available, otherwise computes by scanning.
- `bpobj_space_range()` computes space for block births in `(mintxg, maxtxg]`.

## Control Flow

The object data area stores serialized block pointers. The bonus buffer stores `bpobj_phys_t` accounting and subobject metadata. `bpo_epb` is derived from the data block size.

`bpobj_iterate_impl()` walks block pointers in reverse index order. When freeing, it dirties the bonus buffer, subtracts block accounting, decrements the block count, and later frees the processed DMU range. If subobjects exist, it opens each recursively, optionally accounts before/after space, frees empty processed subobjects, decrements subobject count, and frees processed subobject-array ranges.

`bpobj_enqueue()` stores a compressed-friendly copy of the block pointer: embedded payloads are stripped while preserving relevant fields, non-dedup checksums are cleared, and fill count is dropped. It uses a cached data buffer for append locality.

`bpobj_enqueue_subobj()` avoids storing the shared empty bpobj, discards empty subobjects, and flattens sub-subobjects when their subobject array occupies a single block.

## Dependencies

Depends on DMU object allocation, bonus buffers, `dmu_buf_hold/rele`, `dmu_write`, `dmu_free_range`, `dmu_object_info/free`, ZAP pool-directory entries, SPA feature activation, block pointer size/accounting macros, pool version gates, and `dsl_pool_sync_context()`.

## Invariants And Risks

- The shared empty bpobj must not be modified or freed through ordinary bpobj paths.
- `bpobj_free()` assumes recursive subobject cleanup before freeing the parent object.
- When freeing entries, bytes/compressed/uncompressed counters must track every removed block pointer and subobject delta.
- Old pool versions may lack compressed/uncompressed accounting, forcing scan-based `bpobj_space()`.
- Reverse iteration and cached dbuf offsets assume append-only object layout.
- The stored bp may intentionally differ from the input bp to improve compression; accounting still uses the original bp.
