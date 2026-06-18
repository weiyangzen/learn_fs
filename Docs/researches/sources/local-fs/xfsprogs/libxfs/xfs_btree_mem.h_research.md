# File Research: sources/local-fs/xfsprogs/libxfs/xfs_btree_mem.h

## Purpose

`xfs_btree_mem.h` declares the in-memory xfile-backed btree interface. It defines xfile btree block numbers, address conversion helpers, the `struct xfbtree` header, and function declarations for memory-backed btree operations.

The file is byte-identical to the Linux-stable copy in this repository.

## Address Model

`xfbno_t` is a 64-bit xfile btree block number.

Constants derive xfile btree block sizing from xmbuf block sizing:

- `XFBNO_BLOCKSIZE`
- `XFBNO_BBSHIFT`
- `XFBNO_BBSIZE`

Conversion helpers:

- `xfbno_to_daddr`
- `xfs_daddr_to_xfbno`

These convert between xfile btree block numbers and XFS disk-address units so the generic buffer/btree code can address memory-backed blocks through normal buffer interfaces.

## `struct xfbtree`

`struct xfbtree` stores:

- memory buffer target;
- highest block number written;
- owner value;
- generic root pointer;
- tree height;
- max records for leaf/node blocks;
- min records for leaf/node blocks.

This structure is the root context stored in `cur->bc_mem.xfbtree`.

## Conditional API

When `CONFIG_XFS_BTREE_IN_MEM` is enabled, the header exposes:

- block verification: `xfbtree_verify_bno`;
- root operations: `xfbtree_set_root`, `xfbtree_init_ptr_from_cur`;
- cursor duplication;
- min/max record callbacks;
- block allocation/free callbacks;
- initialization/destruction;
- transaction commit/cancel helpers.

When the config is disabled, `xfbtree_verify_bno` is defined as always false, preventing accidental validation success without memory-btree support.

## Dependencies

The header depends on xmbuf constants and generic btree cursor/types. It is consumed by `xfs_btree.c`, `xfs_btree_mem.c`, and concrete in-memory btree users.
