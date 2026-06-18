# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/block_list.c

## Purpose
Implements a simple list of special block numbers for fsck bookkeeping.

## Main Elements
- `special_free()`: deletes and frees all entries.
- `blockfind()`: linear search for a block number.
- `special_add()`: allocates and appends a block entry.
- `special_set()`: idempotently adds a block if not already present.

## Dependencies And Integration
Uses `osi_list_t` embedded in `struct special_blocks` from `fsck.h`.

## Risk Notes
Allocation failure in `special_add()` is silent; the block is simply not recorded.
