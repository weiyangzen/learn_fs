# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_btree.h

## Purpose

`xfs_btree.h` declares the generic XFS btree interface, cursor structure, operation callbacks, common key/record/pointer unions, geometry flags, comparison helpers, traversal/query prototypes, verification prototypes, and cursor allocation helpers.

It is the contract between concrete XFS btree implementations and the generic engine in `xfs_btree.c`.

## Core Types

The file defines generic on-disk wrapper unions:

- `union xfs_btree_ptr`: short 32-bit AG pointers or long 64-bit pointers.
- `union xfs_btree_key`: key storage for bmbt, allocbt, inobt, rmapbt, refcountbt, and overlapping rmap high/low key storage.
- `union xfs_btree_rec`: record storage for the same btree families.
- `union xfs_btree_irec`: in-core record storage for generic query/update APIs.

The generic code treats these as opaque blobs whose size and interpretation are provided by `xfs_btree_ops`.

## `struct xfs_btree_ops`

`xfs_btree_ops` is the concrete btree vtable. It supplies:

- Name, type, geometry flags, key length, pointer length, record length, stats offset, health mask, and buffer verifier ops.
- Cursor duplication and optional cursor state update.
- Root pointer update callback.
- Block allocation/free callbacks.
- Minimum, maximum, and on-disk-root maximum record calculations.
- Record/key/pointer initialization callbacks.
- Key comparison callbacks against cursor state and against other keys.
- Key order, record order, and key-contiguity validators.
- Optional inode-root reallocation callback.

The generic engine depends on these callbacks for every type-specific decision.

## Geometry Flags

The header defines:

- `XFS_BTGEO_OVERLAPPING`: internal nodes store low/high keys for interval-overlap searches.
- `XFS_BTGEO_IROOT_RECORDS`: inode-rooted root blocks may directly store records.

These flags affect block layout, key propagation, root growth, bulk loading, range queries, and root conversion.

## Cursor Structure

`struct xfs_btree_cur` collects all state needed by generic btree operations:

- Current transaction and mount.
- Operation table and cursor cache.
- Feature flags.
- Current in-core record value.
- Current and maximum tree height.
- Optional group reference.
- Type-specific state for inode, AG, and in-memory btrees.
- Bmap/refcount private accounting fields.
- Per-level buffer pointer, entry pointer, and readahead state.

`bc_levels[]` is a flexible array and must be last. `xfs_btree_cur_sizeof` computes allocation size for a chosen height.

## Cursor Flags

Important flags include:

- `XFS_BTREE_STAGING`: cursor points at fake roots during rebuild/bulk load.
- `XFS_BTREE_BMBT_WASDEL`: bmap cursor is converting a delayed allocation reservation.
- `XFS_BTREE_BMBT_INVALID_OWNER`: skip bmap owner verification during extent swap.
- `XFS_BTREE_ALLOCBT_ACTIVE`: allocation btree cursor activity marker.

The generic code uses these flags to restrict staging operations, verify ownership, and preserve bmap-specific behavior.

## Public Operations

The header exposes generic btree APIs:

- Cursor lifecycle: `xfs_btree_del_cursor`, `xfs_btree_dup_cursor`, `xfs_btree_alloc_cursor`.
- Navigation: `xfs_btree_lookup`, `xfs_btree_increment`, `xfs_btree_decrement`, `xfs_btree_goto_left_edge`.
- Modification: `xfs_btree_update`, `xfs_btree_insert`, `xfs_btree_delete`, `xfs_btree_new_iroot`.
- Record access: `xfs_btree_get_rec`.
- Block access: `xfs_btree_get_block`, `xfs_btree_lookup_get_block`, `xfs_btree_get_buf_block`, `xfs_btree_read_buf_block`.
- Layout access: record/key/high-key/pointer address helpers.
- Query/scan: `xfs_btree_query_range`, `xfs_btree_query_all`, `xfs_btree_has_records`, `xfs_btree_has_more_records`.
- Block walking: `xfs_btree_visit_blocks`, `xfs_btree_count_blocks`, `xfs_btree_change_owner`.
- Sizing: `xfs_btree_compute_maxlevels`, `xfs_btree_calc_size`, `xfs_btree_space_to_height`.
- CRC and verifier helpers for short, long, and in-memory blocks.
- Metadata inode btree block allocation/free helpers.

## Inline Helpers

The header includes inline helpers for:

- Getting/setting `bb_numrecs`.
- Getting block level.
- Pointer null/equality support through declarations.
- Key comparison wrappers around `cmp_two_keys`.
- Masked key comparison wrappers.
- Determining if the cursor is on the last block at a level.
- Determining if a cursor level is the inode-root block via `xfs_btree_at_iroot`.
- Allocating a zeroed cursor from the concrete cursor cache.

## Query Contracts

`xfs_btree_query_range_fn` callbacks return zero to continue or nonzero to stop. `-ECANCELED` is explicitly documented as a normal stop-iteration signal because the query path does not generate it independently.

`xfs_btree_has_records` reports record packing through `enum xbtree_recpacking` and can accept a key mask for comparisons over only selected fields, used by callers such as reverse-mapping scans.

## Integration Points

Concrete btree code must include this header to create cursors, fill `xfs_btree_ops`, and invoke generic traversal/modification. Other XFS subsystems use the exported query and walk helpers to inspect or transform btrees without knowing the concrete block layout.

## Important Invariants

- `ops->ptr_len` must be either `XFS_BTREE_LONG_PTR_LEN` or `XFS_BTREE_SHORT_PTR_LEN`.
- `bc_levels[]` has exactly `bc_nlevels` active entries.
- Inode-root detection is based on btree type and top level.
- Operation callbacks must agree on key, pointer, record sizes and comparison semantics.
- Overlapping btrees must provide high-key initialization and proper key-contiguity behavior.
