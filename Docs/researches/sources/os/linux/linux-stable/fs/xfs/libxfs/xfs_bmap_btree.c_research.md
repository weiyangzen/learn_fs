# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_bmap_btree.c

## Purpose

`xfs_bmap_btree.c` implements the btree backend for XFS inode block mappings. It provides bmap btree block initialization, root conversion between on-disk and in-core formats, packed extent record encoding/decoding, generic btree operation callbacks, block allocation/freeing, verifier operations, inode-root reallocation, staged btree commit, owner changes, sizing helpers, and cursor slab lifecycle.

## Record Format Handling

The file encodes and decodes compact bmap extent records:

- `xfs_bmbt_disk_get_all` extracts logical start offset, physical start block, block count, and unwritten/written state from the two 64-bit record words.
- `xfs_bmbt_disk_get_blockcount` and `xfs_bmbt_disk_get_startoff` extract individual fields.
- `xfs_bmbt_disk_set_all` packs an in-core `xfs_bmbt_irec` back into disk format with assertions for field width and state validity.

These helpers are used throughout bmap code and by btree callbacks.

## Root Format Conversion

Inode-root bmap btrees have a compact on-disk dinode-root form and a fuller in-core btree block form:

- `xfs_bmdr_to_bmbt` converts on-disk root data into in-core root form, copying keys and pointers.
- `xfs_bmbt_to_bmdr` converts the in-core root back to dinode-root form and asserts root-level invariants.
- `xfs_bmap_broot_realloc` resizes the in-core root buffer and moves pointer arrays when the number of root records changes.

## Generic Btree Integration

`xfs_bmbt_ops` supplies the generic XFS btree layer with callbacks for:

- Cursor duplication and update.
- Btree block allocation and freeing.
- Maximum/minimum record counts for root and non-root levels.
- Key initialization from records.
- Record initialization from cursor state.
- Key comparison and record ordering checks.
- Buffer verification operations.
- Key contiguity checks.
- Inode-root reallocation.

`xfs_bmbt_init_cursor` allocates and initializes an inode btree cursor for a data or attr fork, or a staging cursor. CoW fork cursors are rejected by assertion.

## Btree Block Allocation and Freeing

`xfs_bmbt_alloc_block` allocates one filesystem block for a bmap btree split or growth. It:

- Uses inode bmbt owner information for rmap ownership.
- Honors delayed-allocation conversion via `XFS_BTREE_BMBT_WASDEL`.
- Fails with `-ENOSPC` if no block reservation exists for non-delalloc growth.
- Uses `xfs_bmapi_minleft` to try to keep enough space in one AG for a full split.
- Falls back into transaction low-space mode if needed.
- Updates cursor allocation count, inode block count, inode logging, and quota.

`xfs_bmbt_free_block` frees a btree block through deferred extent freeing and reverses inode block/quota accounting.

## Verification and Ordering

The bmap btree verifier checks:

- Magic number and CRC/header validity where applicable.
- Level not exceeding mount-computed maximum bmap levels.
- Generic fsblock btree shape and record limits.

Read and write verifiers report CRC or corruption errors and emit btree corruption traces. Ordering callbacks enforce increasing keys and non-overlapping, logically ordered records.

## Sizing Helpers

- `xfs_bmbt_maxrecs` computes record capacity for a bmap btree block after subtracting the block header.
- `xfs_bmbt_maxlevels_ondisk` computes the maximum supported btree height for all possible filesystems and large extent counts.
- `xfs_bmdr_maxrecs` computes dinode-root capacity.
- `xfs_bmbt_calc_size` estimates btree blocks needed for a number of records.

These feed mount geometry, fork conversion, transaction reservation, and cursor allocation.

## Staging and Owner Change

`xfs_bmbt_commit_staged_btree` replaces a real inode fork with a staged rebuilt fork, logs the correct extent or btree-root fork fields, and commits fake-root state through the generic staging layer.

`xfs_bmbt_change_owner` walks a btree-format fork and changes btree block owner metadata. It supports transactional or recovery-style caller contexts.

## Cache Lifecycle

`xfs_bmbt_init_cur_cache` creates the `xfs_bmbt_cur` slab cache sized for the maximum possible on-disk bmap btree height. `xfs_bmbt_destroy_cur_cache` destroys it.

## Dependencies

This file depends on generic XFS btree infrastructure, transaction and quota accounting, allocation/freeing, rmap owner metadata, inode fork geometry, buffer verifiers, tracepoints, and staging btree support.

## Research Notes

The file is a narrow but critical support layer for `xfs_bmap.c`. Bugs here tend to affect btree-format files broadly: corrupt packed record encoding, root pointer movement, max-record calculations, or verifier behavior can break mapping lookup, allocation, repair, or recovery across any large-extent file.
