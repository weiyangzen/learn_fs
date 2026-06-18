# File Research: sources/os/linux/linux-stable/fs/hfs/btree.h

## Scope

Declares the classic HFS B-tree in-memory structures, find cursor, node flags, lock class enum, and cross-file B-tree APIs.

## Key Structures

- `struct hfs_btree` stores the superblock, special tree inode, key comparator, root/leaf/node/free counts, attributes, node sizing, tree mutex, page count per bnode, hash lock, and bnode hash table.
- `struct hfs_bnode` stores tree linkage, sibling/parent IDs, node type/height, record count, hash linkage, state flags, waitqueue, refcount, page offset, and backing pages.
- `struct hfs_find_data` is the shared cursor used by search and mutation paths: active/search keys, tree, current bnode, record index, and key/entry offsets and lengths.

## API Surface

The header exposes B-tree open/close/write and bmap allocation, low-level bnode read/write/copy/move/refcount routines, B-tree record insertion/removal, and search/read/goto helpers from `bfind.c`.

## Risks And Invariants

The header makes the locking model visible: callers generally enter through `hfs_find_init()` and hold `tree_lock` while using `hfs_find_data`. Bnodes are refcounted and hash-cached, so any path storing `fd->bnode` must pair with `hfs_find_exit()` or explicit `hfs_bnode_put()`.
