# File Research: sources/local-fs/xfsprogs/libxfs/xfs_btree.h

## Purpose

`xfs_btree.h` is the public generic btree interface for libxfs. It defines the generic pointer, key, record, incore-record, cursor, operation-vector, traversal, query, verification, and helper APIs used by all XFS btree implementations.

The header is byte-identical to the Linux-stable copy in this repository.

## Generic Disk Wrappers

The file defines generic disk-format unions:

- `union xfs_btree_ptr`: short 32-bit AG block pointers or long 64-bit pointers.
- `union xfs_btree_key`: allocation, inode allocation, bmap, rmap, and refcount key storage.
- `union xfs_btree_rec`: allocation, inode allocation, bmap, rmap, and refcount record storage.

Overlapping btrees reserve enough key space for low/high key pairs.

`union xfs_btree_irec` defines incore records used by callers before concrete btree ops convert them to disk-format records and keys.

## Operation Vector

`struct xfs_btree_ops` is the core plug-in contract for concrete btrees. It supplies:

- btree name and type;
- geometry flags;
- key, pointer, and record sizes;
- buffer ops;
- stats and health metadata;
- cursor duplication/update callbacks;
- root pointer update callback;
- block allocation/free callbacks;
- min/max/disk-max record calculations;
- record/key initialization callbacks;
- key comparison callbacks;
- order checks for debug validation;
- key contiguity callback for sparse/full range classification;
- inode fork-root reallocation callback.

Geometry flags include:

- `XFS_BTGEO_OVERLAPPING`: internal nodes store interval summaries.
- `XFS_BTGEO_IROOT_RECORDS`: inode fork roots can store records directly.

## Cursor Structure

`struct xfs_btree_cur` carries transaction, mount, ops, cache, flags, current incore record, current height, max height, group reference, type-specific root context, per-format private counters, and a flexible array of `struct xfs_btree_level`.

Per-type cursor context includes:

- inode-rooted cursor state: inode, fork size, fork selector, staging fake root;
- AG-rooted cursor state: AG buffer and AG fake root;
- memory-backed cursor state: `struct xfbtree`.

Per-level state includes:

- current buffer;
- one-based current key/record pointer;
- left/right sibling readahead flags.

`xfs_btree_cur_sizeof` computes the allocation size for a cursor with a given height.

## Cursor Flags

Defined cursor flags include:

- `XFS_BTREE_STAGING`: cursor root is a fake staging root.
- `XFS_BTREE_BMBT_WASDEL`: bmap conversion from delayed allocation.
- `XFS_BTREE_BMBT_INVALID_OWNER`: skip owner check for extent swap.
- `XFS_BTREE_ALLOCBT_ACTIVE`: active allocation btree cursor.

## Exported Core APIs

The header declares generic operations implemented in `xfs_btree.c`:

- cursor lifecycle: `xfs_btree_del_cursor`, `xfs_btree_dup_cursor`;
- block verification: `xfs_btree_check_block`, `__xfs_btree_check_block`, `__xfs_btree_check_ptr`;
- block initialization: `xfs_btree_init_buf`, `xfs_btree_init_block`, `xfs_btree_init_block_cur`;
- lookup and movement: `xfs_btree_lookup`, `xfs_btree_increment`, `xfs_btree_decrement`;
- mutation: `xfs_btree_update`, `xfs_btree_insert`, `xfs_btree_delete`, `xfs_btree_new_iroot`;
- traversal and query: `xfs_btree_query_range`, `xfs_btree_query_all`, `xfs_btree_visit_blocks`;
- block counting and owner rewrite;
- CRC helpers;
- geometry helpers;
- cursor cache initialization/destruction;
- metadata-file block allocation/free helpers.

## Inline Helpers

The header provides inline helpers for:

- getting and setting `bb_numrecs`;
- reading block level;
- min/max macros for XFS numeric types;
- key comparisons with and without masks;
- determining whether a cursor is at an inode-rooted fork root;
- testing whether a cursor points to the last block at a level;
- allocating cursors from concrete cursor caches.

`xbtree_key_contig` classifies adjacent numeric key fields as gap, contiguous, or overlap and underpins `xfs_btree_has_records`.

## Traversal and Query Contracts

`xfs_btree_query_range_fn` callbacks receive each matching record and return zero to continue or nonzero to stop. `-ECANCELED` is reserved as an intentional stop code because query code does not generate it internally.

`xfs_btree_visit_blocks_fn` callbacks receive each visited block and its level. Flags select record blocks, leaf/internal blocks, or all blocks.

## Dependencies

This header is the central API shared by all concrete XFS btree implementations, in-memory btree support, and staging/bulk-load code.
