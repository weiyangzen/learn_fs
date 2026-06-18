# File Research: sources/local-fs/xfsprogs/libxfs/xfs_bmap_btree.c

## Purpose

`xfs_bmap_btree.c` implements the bmap btree-specific adapter for XFS generic btree code. It handles bmap btree block initialization, root conversion between dinode and incore formats, packed extent record encode/decode, btree cursor allocation, block allocation/free callbacks, record/key comparison, verifier operations, root reallocation, staged btree commit, owner changes, btree size calculation, and cursor cache lifecycle.

## Btree Block Initialization

`xfs_bmbt_init_block` initializes either a buffer-backed btree block or an incore block using `xfs_btree_init_buf` or `xfs_btree_init_block`. The inode number is supplied as the owner for bmap btree blocks.

## Root Format Conversion

Bmap btree roots live inside inode forks in a compact on-disk `xfs_bmdr_block` layout, but are manipulated incore as normal btree blocks.

- `xfs_bmdr_to_bmbt` converts dinode root format to incore btree root format.
- `xfs_bmbt_to_bmdr` converts incore btree root format back to dinode root format.

The conversion copies level, record count, keys, and pointers. CRC filesystems verify magic, uuid, null block number, and null siblings before converting back.

## Packed Extent Records

Bmap extent records are stored as two big-endian 64-bit words.

- `xfs_bmbt_disk_get_all` unpacks start offset, start block, block count, and unwritten state.
- `xfs_bmbt_disk_get_blockcount` extracts block count.
- `xfs_bmbt_disk_get_startoff` extracts logical start offset.
- `xfs_bmbt_disk_set_all` packs an incore `xfs_bmbt_irec` into disk format.

The packed layout stores:

- one high-bit unwritten flag
- logical file offset
- physical start block
- block count

Assertions ensure fields fit their on-disk bit widths and state is either normal or unwritten.

## Generic Btree Operations

The file defines `xfs_bmbt_ops`, an `xfs_btree_ops` instance for bmap btrees. It supplies:

- cursor duplication and update
- block allocation and free
- max/min record calculations
- dmax record calculation for inode-root capacity
- key initialization from records
- high-key initialization
- record initialization from cursor
- key comparison
- buffer verifier operations
- key/record ordering predicates
- key contiguity predicate
- inode root reallocation callback

This is the bridge between generic btree algorithms and bmap-specific record semantics.

## Block Allocation and Freeing

`xfs_bmbt_alloc_block` allocates one filesystem block for a bmap btree split. It sets rmap owner info for inode bmbt ownership, respects delayed allocation context through `XFS_BTREE_BMBT_WASDEL`, handles no-reservation cases, uses `minleft` when no AG has been selected yet, and can fall back to low-space mode. On success it increments cursor allocation count, inode block count, logs inode core, and updates quota.

`xfs_bmbt_free_block` schedules a bmap btree block for deferred freeing, decrements inode block count, logs inode core, and updates quota.

## Record Capacity

Capacity helpers include:

- `xfs_bmbt_get_minrecs`
- `xfs_bmbt_get_maxrecs`
- `xfs_bmbt_get_dmaxrecs`
- `xfs_bmbt_maxrecs`
- `xfs_bmdr_maxrecs`
- `xfs_bmbt_maxlevels_ondisk`
- `xfs_bmbt_calc_size`

Root capacity depends on inode fork space, while non-root block capacity depends on filesystem block size and btree block header size. CRC-enabled filesystems use larger btree headers.

## Verification

The buffer ops `xfs_bmbt_buf_ops` provide read/write/struct verification for bmap btree blocks.

`xfs_bmbt_verify` checks:

- btree magic
- CRC header fields when applicable
- level bounded by maximum data/attr bmap levels
- generic fsblock btree structure and record count

Read verification also checks CRC; write verification recalculates CRC after structural validation.

## Root Reallocation

`xfs_bmap_broot_realloc` resizes the incore inode btree root buffer based on target record count. It handles:

- freeing the root when record count becomes zero
- initial allocation
- growth by moving pointer arrays to their new offset
- shrink by moving pointer arrays before reallocating

Bmap root records are packed after the header, while pointers live after the key array, so pointer movement is required whenever root capacity changes.

## Cursor Lifecycle

`xfs_bmbt_init_cursor` allocates a generic btree cursor configured for bmap btrees. It rejects CoW fork cursors, supports staging cursors, initializes maximum levels, stores inode/fork context, and derives current btree level count from the fork root.

`xfs_bmbt_init_cur_cache` and `xfs_bmbt_destroy_cur_cache` manage the slab cache for bmap btree cursors sized to the maximum possible on-disk level count.

## Staged Btree Commit

`xfs_bmbt_commit_staged_btree` replaces a real inode fork with a staged fake-root fork after rebuilding mappings. It destroys the old fork resources, shallow-copies the staged fork, logs the correct inode fields based on extent or btree format, and commits staged btree blocks.

## Owner Changes

`xfs_bmbt_change_owner` walks a btree-format fork to change btree block owner metadata. It supports either transactional modification or recovery-style buffer-list output, but not both simultaneously.

## Research Notes

This file is intentionally narrow: it does not decide mapping policy, but it makes generic btree machinery understand XFS bmap records. The most important correctness surfaces are packed record encoding, root reallocation pointer movement, block allocation accounting, and verifier strictness.
