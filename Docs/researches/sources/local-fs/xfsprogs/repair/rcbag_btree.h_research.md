# File Research: sources/local-fs/xfsprogs/repair/rcbag_btree.h

## Role

`rcbag_btree.h` defines the record layout, block addressing macros, and public helper API for the in-memory refcount bag btree.

## Data Structures

- `RCBAG_MAGIC` identifies refcount bag btree blocks.
- `struct rcbag_key` contains `startblock`, `blockcount`, and `ino`.
- `struct rcbag_rec` adds `refcount` to the key fields.
- `rcbag_ptr_t` is the long-pointer type used by internal btree blocks.
- `RCBAG_REC_ADDR`, `RCBAG_KEY_ADDR`, and `RCBAG_PTR_ADDR` compute on-block addresses.

## Interface

The header declares sizing helpers, cursor-cache lifecycle, memory cursor creation, memory tree initialization, and lookup/get/update/insert operations.

## Dependencies

It references libxfs btree, mount, transaction, buffer target, and xfbtree types.

## Risk Areas

The record/key layouts are cast into libxfs btree unions, so size and ordering assumptions must remain compatible with the generic btree code.
