# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_bmap_btree.c

## Purpose

`xfs_bmap_btree.c` implements the btree backend for XFS inode block mappings. It supplies record encoding/decoding, root conversion, generic btree callbacks, block allocation/freeing, verifiers, inode-root reallocation, staged btree commit, owner changes, sizing helpers, and cursor cache lifecycle for bmap btrees.

The high-level bmap code uses this file when inode fork extent arrays outgrow inline extent format.

## Major Responsibilities

- Initialize bmap btree blocks with inode ownership.
- Convert between on-disk dinode-root format and in-core btree root format.
- Encode and decode packed bmap extent records.
- Provide `xfs_bmbt_ops` callbacks to the generic XFS btree layer.
- Allocate and free bmap btree blocks with inode and quota accounting.
- Verify bmap btree buffers, magic values, CRC headers, levels, and record counts.
- Resize in-core inode btree roots while moving pointer arrays.
- Commit staged rebuilt btrees into real inode forks.
- Change btree block owner values for fork swaps and recovery workflows.
- Calculate btree sizes and maximum levels.
- Initialize and destroy the bmap btree cursor slab cache.

## Record Encoding

Bmap extent records are packed across two 64-bit fields. Helpers include:

- `xfs_bmbt_disk_get_all`
- `xfs_bmbt_disk_get_blockcount`
- `xfs_bmbt_disk_get_startoff`
- `xfs_bmbt_disk_set_all`

The packed fields store extent state, file offset, start block, and block count. `xfs_bmbt_disk_set_all` asserts that state and bit widths fit the on-disk format.

## Root Conversion

`xfs_bmdr_to_bmbt` converts an on-disk dinode root into an in-core btree root. `xfs_bmbt_to_bmdr` converts the in-core root back to dinode-root format and checks CRC-era root invariants when applicable.

These conversions copy key and pointer arrays between layouts whose header sizes and pointer locations differ.

## Generic Btree Integration

`xfs_bmbt_ops` wires bmap btrees into the generic XFS btree implementation. It provides callbacks for:

- cursor duplication and update
- block allocation and freeing
- min/max record calculations
- root maximum record calculations
- key initialization and comparison
- record initialization
- buffer verifier operations
- key and record ordering checks
- key contiguity checks
- inode-root reallocation

`xfs_bmbt_init_cursor` creates cursors for data, attr, or staging forks. It rejects CoW forks and sizes staging cursors using the data fork maximum level.

## Block Allocation and Freeing

`xfs_bmbt_alloc_block` allocates one filesystem block for bmap btree growth, sets inode bmbt rmap owner information, observes delayed-allocation conversion state, handles zero block-reservation cases, and can activate transaction low-space mode. Successful allocation increments cursor allocation count, inode block count, quota, and inode log state.

`xfs_bmbt_free_block` schedules the btree block for freeing, decrements inode block count, logs the inode, and updates quota.

## Verification

`xfs_bmbt_verify` checks block magic, CRC-era block headers, maximum btree level, and generic btree block structure. Read and write verifiers wrap this with CRC verification or CRC calculation and emit btree corruption traces on failure.

`xfs_bmbt_keys_inorder` and `xfs_bmbt_recs_inorder` enforce strict key order and non-overlapping extent records.

## Inode Root Reallocation

`xfs_bmap_broot_realloc` grows, shrinks, or frees the in-core inode btree root according to a target record count. Because bmap root records and pointers are stored in separate arrays, pointer arrays must be moved when the root size changes.

This is layout-sensitive code: growing creates pointer holes for callers to fill, while shrinking compacts pointers before reallocating the root buffer.

## Staged Btree Commit

`xfs_bmbt_commit_staged_btree` replaces a real inode fork with a staged rebuilt fork, logs the appropriate extent or btree root fields, and commits the fake root through the generic btree staging layer. This is used by repair/rebuild style workflows that construct a replacement tree before making it live.

## Owner Changes and Sizing

`xfs_bmbt_change_owner` walks a btree-format fork and changes btree block owner metadata, either transactionally or by collecting buffers for recovery-style writeout.

Sizing helpers include:

- `xfs_bmbt_maxrecs`
- `xfs_bmbt_maxlevels_ondisk`
- `xfs_bmdr_maxrecs`
- `xfs_bmbt_calc_size`

## Notable Invariants

- CoW fork bmap btree cursors are not supported.
- Bmap btree blocks are owned as inode bmbt metadata.
- Btree block allocation is accounted to inode blocks and quota.
- Root and non-root block capacities are calculated differently.
- The inode root has in-core and on-disk layouts with different headers.
- Packed record fields must stay within their defined bit widths.
- Verifier level checks use the maximum of data and attr fork maxlevels because the verifier does not know the fork.

## Research Notes

This file is narrow but critical. Bugs in record packing, root pointer movement, max-record calculation, ownership changes, or verifier behavior can corrupt large-extent files and can break recovery, repair, or fork conversion paths.
