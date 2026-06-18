# File Research: sources/os/linux/linux-stable/fs/hfsplus/bnode.c

## Scope

Implements HFS+ low-level B-tree node IO, memory movement, validation, hash-cache lookup, creation, refcounting, unlinking, and deletion cleanup.

## APIs And Behavior

- `hfs_bnode_read/write/clear/copy/move()` operate on bnode byte ranges across one or more page-cache pages, validate offsets/lengths, and mark modified pages dirty.
- `hfs_bnode_read_key()` reads variable or fixed-length keys, with attributes-tree special handling and maximum size validation.
- `hfs_bnode_dump()` emits debug details about node descriptors and record offsets.
- `hfs_bnode_unlink()` updates previous/next sibling links, leaf head/tail, root/depth for root deletion, and marks the node deleted.
- `hfs_bnode_findhash()` and `hfs_bnode_find()` implement cached bnode lookup and loading from the tree inode.
- `hfs_bnode_find()` validates node type/height, first offset, monotonic even record offsets, and key sizes for index/leaf records.
- `hfs_bnode_create()` creates a new zeroed bnode and clears the `NEW` flag after initialization.
- `hfs_bnode_put()` frees deleted nodes by unhashing, optionally zeroing contents, freeing the bmap bit, and releasing pages.
- `hfs_bnode_need_zeroout()` checks the volume unused-node-fix attribute for catalog-tree zeroing.

## State And Dependencies

This file owns the bnode hash/refcount/waitqueue protocol and depends on page cache, B-tree geometry, bmap free, node validation helpers, and volume header attributes.

## Risks And Invariants

Concurrent loads of the same node synchronize through `HFS_BNODE_NEW` and `lock_wq`. A malformed node causes `HFS_BNODE_ERROR` and `-EIO`. Deleted nodes are not physically freed until the last ref drops, and freeing requires the tree mutex because it clears the bmap bit.
