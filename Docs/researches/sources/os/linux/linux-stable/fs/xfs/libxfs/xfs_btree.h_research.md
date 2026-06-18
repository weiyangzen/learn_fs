# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_btree.h

## Role in the repository

`xfs_btree.h` declares the generic XFS btree interface, cursor structure, operation callback table, common key/record/pointer unions, traversal/query APIs, verification helpers, and utility inline functions used by all XFS btree implementations.

## Disk-format wrapper unions

The header defines generic wrappers around concrete btree formats:
- `union xfs_btree_ptr` stores either a short big-endian AG block pointer (`__be32 s`) or long big-endian filesystem/xfile block pointer (`__be64 l`).
- `union xfs_btree_key` contains key formats for bmap, allocation, inode allocation, rmap, and refcount btrees. It also reserves doubled rmap key storage for overlapping btrees.
- `union xfs_btree_rec` contains record formats for the same btree families.
- `union xfs_btree_irec` stores incore record representations for allocation, bmap, inode allocation, rmap, and refcount operations.

These unions let the core btree code copy and address opaque records while concrete btree implementations interpret contents.

## Operation table

`struct xfs_btree_ops` is the central contract between the generic engine and concrete btree types. It defines:
- The btree name, type, geometry flags, key/pointer/record sizes, LRU refs, stats offset, and health mask.
- Cursor duplication and optional cursor-state update callbacks.
- Root update callbacks.
- Block allocation/free callbacks.
- Minimum, maximum, and disk-root maximum record calculations.
- Callbacks to initialize keys, high keys, records, and root pointers.
- Key comparison, key ordering, record ordering, and contiguity callbacks.
- Buffer verifier ops.
- Optional inode-root reallocation callback.

The callback table is what allows one implementation in `xfs_btree.c` to drive AG btrees, inode btrees, realtime btrees, and memory-backed btrees.

## Geometry and type flags

`enum xfs_btree_type` distinguishes AG-rooted, inode-rooted, and in-memory btrees. The geometry flags are:
- `XFS_BTGEO_OVERLAPPING`, for interval btrees with low/high keys.
- `XFS_BTGEO_IROOT_RECORDS`, for inode-rooted btrees whose in-inode root can store records.

`enum xbtree_key_contig` and `xbtree_key_contig` classify numeric key fields as gap, contiguous, or overlapping. This supports range coverage checks and sparse/full classification.

## Cursor state

`struct xfs_btree_cur` stores all mutable traversal and mutation state:
- Transaction, mount, operation table, cursor cache, flags, current incore record, current height, maximum height, and optional group reference.
- Per-type state for inode-rooted, AG-rooted, and memory-backed btrees.
- Per-format private counters for bmap and refcount cursors.
- A flexible array of `struct xfs_btree_level` entries, one per tree level.

Each `xfs_btree_level` stores a buffer pointer, one-based key/record index, and sibling readahead flags.

Cursor flags include:
- `XFS_BTREE_STAGING`, meaning the cursor points to a fake root used by rebuild/bulk load.
- `XFS_BTREE_BMBT_WASDEL`, for bmap delalloc conversion.
- `XFS_BTREE_BMBT_INVALID_OWNER`, for extent swap owner-check suppression.
- `XFS_BTREE_ALLOCBT_ACTIVE`, for active allocation btree cursor state.

`xfs_btree_cur_sizeof` computes cursor allocation size for a given height. `xfs_btree_alloc_cursor` allocates a zeroed cursor from a kmem cache, stores common fields, and intentionally uses `__GFP_NOFAIL` because bmap allocations can arise in contexts where failure handling is not feasible.

## Public API surface

The header declares the main generic operations:
- Cursor lifecycle: `xfs_btree_del_cursor`, `xfs_btree_dup_cursor`.
- Navigation and search: `xfs_btree_lookup`, `xfs_btree_increment`, `xfs_btree_decrement`, `xfs_btree_goto_left_edge`.
- Mutation: `xfs_btree_update`, `xfs_btree_insert`, `xfs_btree_delete`, `xfs_btree_new_iroot`.
- Record access: `xfs_btree_get_rec`.
- Query and traversal: `xfs_btree_query_range`, `xfs_btree_query_all`, `xfs_btree_visit_blocks`, `xfs_btree_count_blocks`, `xfs_btree_has_records`, `xfs_btree_has_more_records`.
- Owner changes: `xfs_btree_change_owner`.
- Geometry calculations: `xfs_btree_compute_maxlevels`, `xfs_btree_calc_size`, `xfs_btree_space_to_height`.
- Buffer/block helpers: block verification, CRC helpers, block address helpers, sibling helpers, copy helpers, and initialization helpers.

The range query callback type `xfs_btree_query_range_fn` returns zero to continue and nonzero to stop. `-ECANCELED` is reserved as a clean early-stop value because the generic range query does not generate it by itself.

## Verification declarations

The header exposes block verifier helpers for:
- Long-format v5 headers and long-format btree blocks.
- Short-format v5 headers and short-format btree blocks.
- Memory-backed btree blocks.

It also exposes internal block and pointer checking helpers used by concrete btree verifiers and debug code.

## Inline helpers

Important inline helpers include:
- `xfs_btree_get_numrecs`, `xfs_btree_set_numrecs`, and `xfs_btree_get_level`.
- Key comparison wrappers around `cmp_two_keys`, including masked variants.
- `xfs_btree_islastblock`, which checks the right sibling pointer.
- `xfs_btree_at_iroot`, which identifies an inode-rooted in-fork root at the top level.

The header also declares shared metafile block allocation/free helpers for inode-rooted metadata btrees.

## Important invariants

- The core requires `ptr_len` to be either `XFS_BTREE_LONG_PTR_LEN` or `XFS_BTREE_SHORT_PTR_LEN`.
- Concrete btree code must supply callbacks that match its geometry and record format.
- Inode-rooted btrees need special handling because the root can be stored in an inode fork instead of a buffer.
- Overlapping btrees must provide high-key initialization and comparison semantics compatible with interval traversal.
