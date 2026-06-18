# File Research: sources/windows/winbtrfs/src/treefuncs.c

## Purpose

`treefuncs.c` implements WinBtrfs' in-memory Btrfs tree node lifecycle and mutation machinery. It loads tree blocks from disk into cached `tree` / `tree_data` structures, traverses B-tree leaves and internal nodes, inserts and deletes metadata items, maintains rollback records for failed filesystem updates, and commits batched metadata changes into dirty in-memory tree nodes.

This file is a core metadata layer used by directory, inode, extent, free-space, root, and chunk management code. It does not write serialized tree blocks by itself; instead it marks tree nodes dirty (`write = true`) and updates generation/size/item counters so later flush code can split/rewrite trees.

## Tree Loading and Cache Management

`load_tree` constructs a `tree` object from a raw tree block buffer already read from disk. It copies the `tree_header`, initializes internal-node locking state, builds the `itemlist`, and inserts the tree into both `Vcb->trees` and the sorted hash list `Vcb->trees_hash`.

Leaf nodes become `tree_data` entries pointing into the backing `buf` payload. Internal nodes become `tree_data` entries with `treeholder.address`, `treeholder.generation`, and a lazily populated child `tree` pointer. The loader validates that item arrays fit within `Vcb->superblock.node_size` and rejects oversized leaf items.

`do_load_tree` allocates a node-sized buffer, calls `read_data` with metadata verification and expected generation, and then serializes child/root installation under either the parent tree mutex or the root `load_tree_lock`. `do_load_tree2` avoids duplicate loads if another thread populated the holder first.

`free_tree`, `free_trees_root`, and `free_trees` tear down cached tree objects. They clear parent/root back-pointers, remove hash/list entries, free inserted leaf data separately from buffer-backed leaf data, and release node buffers/nonpaged locks. `free_trees` also reaps cached file references and FCBs after tree teardown.

## Traversal

The small helpers `first_item`, `prev_item`, `next_item`, and `last_item` wrap list navigation for a `tree`. `find_item_in_tree` performs the main B-tree descent: it finds the last key less than or equal to the search key, lazily loads child blocks, honors the `ignore` flag for logically deleted entries, and can stop at an arbitrary tree level for callers that need an internal node.

Public traversal APIs include:

- `find_item`: finds a leaf-level item at or before the requested key.
- `find_item_to_level`: like `find_item`, but may stop at a caller-specified internal level.
- `find_next_item`: walks to the next leaf item, loading right-side child paths as needed and optionally skipping ignored entries.
- `find_prev_item`: walks to the previous leaf item, loading left-side child paths as needed.
- `skip_to_difference`: advances two traversal pointers until their paths diverge or one side ends; this supports comparing related tree versions.

Important caveat: `find_prev_item` has a FIXME noting that it does not support an ignore flag. Callers relying on visible-only reverse traversal must account for this.

## Direct Item Mutation

`insert_tree_item` inserts one metadata item into a root. It loads the root if needed, rejects duplicate non-ignored keys, allocates a `tree_data`, inserts it in sorted order, updates parent separator keys when inserting before the first key, increments item/size counters, marks the leaf dirty, sets `Vcb->need_write`, and bumps generation on the modified leaf and ancestors.

`delete_tree_item` implements logical deletion by setting `tree_data.ignore`, decrementing the containing tree's visible item count and serialized size, marking the node dirty, and propagating the current superblock generation up the ancestor chain. It does not immediately unlink/free the item.

These direct mutation helpers require the global tree lock to be held exclusively.

## Rollback Support

`add_rollback` appends rollback records to a caller-owned list. `clear_rollback` frees rollback payloads without applying them. `do_rollback` walks the rollback list in reverse order and undoes space-list and extent-list mutations after failed higher-level operations.

Rollback cases cover:

- `ROLLBACK_INSERT_EXTENT`: re-ignores an inserted extent and decrements extent references/st_blocks.
- `ROLLBACK_DELETE_EXTENT`: restores a deleted extent and increments references/st_blocks.
- `ROLLBACK_ADD_SPACE` and `ROLLBACK_SUBTRACT_SPACE`: reverse free-space list and chunk-used accounting changes, coalescing same-chunk rollback records while holding the chunk lock.

Rollback interacts with chunk lookup, changed extent refs, inode `st_blocks`, and free-space list helpers. Error paths mostly log failures from reference updates and continue unwinding.

## Batched Metadata Changes

`clear_batch_list` frees uncommitted batch roots, index buckets, and batch items. `commit_batch_list` drains a list of `batch_root` entries and calls `commit_batch_list_root` for each root.

`commit_batch_list_root` flattens indexed batch sublists into one sorted list, then applies operations into tree leaves. It supports broad delete operations (`Batch_DeleteInode`, `Batch_DeleteExtentData`, `Batch_DeleteFreeSpace`) and point operations such as insert, delete, directory item update, inode ref update, extended inode ref update, xattr set/delete, and free-space item changes.

The function tries to batch consecutive operations that fall before the current leaf's tree-end key, reducing repeated full tree searches. It keeps inserted items sorted, updates counts/sizes, marks touched trees dirty, restores ignored parent separator entries when a child becomes visible again, and propagates the superblock generation upward.

## Collision Handling

`handle_batch_collision` resolves batch operations that target an existing visible item. It has specialized logic for packed Btrfs item types:

- `Batch_SetXattr`: replaces an existing xattr with the same name or appends a new one inside a `DIR_ITEM` payload, truncating to the node max length when needed.
- `Batch_DirItem`, `Batch_InodeRef`, `Batch_InodeExtRef`: appends another packed entry to the existing item payload.
- `Batch_InodeRef`: when an `INODE_REF` would overflow and extended inode refs are enabled, converts the operation into a `Batch_InodeExtRef`.
- `Batch_DeleteDirItem`, `Batch_DeleteInodeRef`, `Batch_DeleteInodeExtRef`, `Batch_DeleteXattr`: removes one packed subrecord, either deleting the whole item or inserting a replacement item with the remaining packed records.
- `Batch_DeleteInodeRef`: if a matching normal inode ref is not found and extended refs are enabled, adds a synthesized `Batch_DeleteInodeExtRef`.

After collision-specific processing, the old item is marked ignored and any replacement `tree_data` is inserted before it.

## Dependencies and Cross-File Interactions

This file depends on structures and helpers from `btrfs_drv.h`, checksum hashing from `crc32c.h`, and the block read path through `read_data`. It is called by metadata update code across the driver, including create/delete, extent-tree updates, free-space management, root updates, directory/xattr updates, and flush logic.

It assumes synchronization from `Vcb->tree_lock` for most public mutation/traversal entry points, uses per-tree fast mutexes during lazy child loading, and uses root load resources for root-node loading.

## Error Handling and Safety Notes

The code consistently returns `STATUS_INSUFFICIENT_RESOURCES` for allocation failures and logs structural corruption or unexpected duplicate keys. Many mutations rely on logical deletion via `ignore`; correct item counts and sizes depend on every collision/delete path decrementing only visible items.

Memory ownership is subtle: original leaf item data points into `tree->buf`, while inserted or replacement item data is separately allocated and freed only when `inserted` is true. Batch collision code transfers `bi->data` ownership into `tree_data` for successful inserts/replacements, while some delete-operation payloads are freed at batch cleanup.

Research follow-up should pair this file with the tree flush/split code, because this file prepares dirty in-memory metadata but does not show how overfull leaves/internal nodes are later serialized.
