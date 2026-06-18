# File Research: sources/windows/reactos/drivers/filesystems/btrfs/treefuncs.c

## Role In The Filesystem

`treefuncs.c` implements core in-memory Btrfs tree operations for the ReactOS/WinBtrfs driver. It loads B-tree nodes from disk, caches them, traverses sorted items, inserts and deletes logical tree items, manages rollback state, and commits batched metadata updates.

This is foundational driver code. Higher-level modules such as send, read/write, extent management, directory handling, and filesystem control rely on these routines to navigate and mutate Btrfs roots safely under the driver tree lock.

## Tree Loading And Cache Registration

`load_tree` converts a raw node buffer into an in-memory `tree` object.

For leaf nodes:

- Validates the item array fits inside the configured node size.
- Allocates one `tree_data` per `leaf_node`.
- Stores item key, size, and a pointer into the raw buffer for item data.
- Tracks aggregate tree payload size.
- Keeps the raw buffer as `t->buf`.

For internal nodes:

- Validates the internal item array fits.
- Allocates one `tree_data` per `internal_node`.
- Stores child address and generation in `treeholder`.
- Does not keep a leaf data buffer.

For both:

- Copies the tree header.
- Initializes parent/root/paritem pointers.
- Initializes write/new-address/extent-update flags.
- Adds the tree to `Vcb->trees`.
- Adds it to `Vcb->trees_hash`, using `trees_ptrs` buckets based on the high byte of a CRC32C hash of the tree address.

`do_load_tree` allocates a node-sized buffer, reads the tree block with `read_data`, serializes child load through either the parent tree mutex or root load lock, then delegates to `do_load_tree2`.

`do_load_tree2` avoids duplicate loads by checking `tree_holder->tree` before calling `load_tree`.

## Tree Freeing

`free_tree` releases one tree:

- Clears the parent item’s `treeholder.tree`.
- Frees inserted leaf item data.
- Returns `tree_data` entries to the lookaside list.
- Removes the tree from global tree lists and hash buckets.
- Clears the root holder if this is the root tree.
- Frees the raw leaf buffer and nonpaged mutex state.

`free_trees_root` frees all cached trees for a specific root level-by-level from leaves upward.

`free_trees` frees all cached trees, then reaps file references and FCBs.

The level-by-level strategy matters because parent/child pointers and root holders must not be left pointing into freed children.

## Traversal Helpers

Local helpers:

- `first_item`
- `last_item`
- `prev_item`
- `next_item`

Public traversal:

- `find_item`
- `find_item_to_level`
- `find_next_item`
- `find_prev_item`
- `skip_to_difference`

`find_item_in_tree` performs the core search. It walks sorted `tree_data` entries, descends through internal nodes as needed, lazy-loads child trees, and respects ignored/deleted items unless the caller asks to include them.

Important behavior:

- If an exact leaf item is ignored and ignored items should be hidden, the function searches backward for a visible predecessor, then forward for a visible successor.
- `find_item_to_level` can stop at an internal level instead of descending to leaves.
- If `find_item_to_level` returns `STATUS_NOT_FOUND`, it still initializes `tp->tree` to the root tree and `tp->item` to `NULL`.

`find_next_item` moves forward in key order across leaves, loading right-hand child paths as needed. It can skip ignored items.

`find_prev_item` moves backward in key order. A FIXME notes it does not support an ignore flag.

`skip_to_difference` is optimized for snapshot comparison. Given traverse pointers in two roots, it climbs until the shared tree address diverges, then advances to the next differing leaf item. This lets send-style code skip whole shared B-tree subtrees.

## Single-Item Insert And Delete

`insert_tree_item` inserts one leaf item into a root:

- Looks up the target key with ignored items visible.
- Handles insertion into an empty tree.
- Rejects an already-present non-ignored item.
- Allocates a `tree_data` entry from the lookaside list.
- Inserts before/after the found item based on key comparison.
- Places a replacement before ignored duplicates so live entries sort before deleted versions.
- Updates `num_items`, tree size, write flags, `Vcb->need_write`, and generations up the parent chain.
- Revives ignored parent items if insertion makes a previously hidden subtree visible.

`delete_tree_item` marks an item ignored rather than immediately unlinking it:

- Sets `item->ignore`.
- Marks tree and Vcb dirty.
- Decrements `num_items`.
- Subtracts item size from aggregate tree size.
- Updates generations up the parent chain.

This lazy-delete model lets later insertion/collision code reason about old and new versions before final writeout.

## Rollback Support

`add_rollback` appends rollback records to a caller-owned list.

`clear_rollback` frees rollback records without applying them. It frees payloads for extent and space rollback types.

`do_rollback` applies rollback records in reverse order. Supported rollback types include:

- Inserted extent: mark ignored, update changed extent refs, subtract inode blocks.
- Deleted extent: unignore, update changed extent refs, add inode blocks.
- Added/subtracted free space: reverse space-list mutation and update chunk usage.

For chunk space rollback, the routine acquires the chunk lock, applies the current rollback, then coalesces and applies earlier rollback records for the same chunk before releasing the lock. This avoids repeated lock cycling and preserves chunk accounting consistency.

## Batch List Structure

Batched metadata changes are grouped by root:

- `batch_root` owns one root and indexed sublists.
- `batch_item_ind` contains a list of `batch_item`s.
- `clear_batch_list` frees all batch roots, sublists, and batch items.

`commit_batch_list` drains batch roots and calls `commit_batch_list_root`.

`commit_batch_list_root` flattens the indexed sublists into one sorted `items` list, then applies items to the in-memory tree.

Batch operations include:

- Generic insert/delete.
- Delete whole inode.
- Delete all extent data for an inode.
- Delete free-space ranges.
- Directory item insert/delete.
- Xattr set/delete.
- Inode ref insert/delete.
- Extended inode ref insert/delete.

## Collision Handling For Packed Items

`handle_batch_collision` resolves batch operations whose key already exists.

Packed Btrfs items may store multiple logical records under one key, so collision does not always mean failure. This function handles:

- `Batch_SetXattr`: replace existing xattr by name or append it.
- `Batch_DirItem`: append a packed directory item.
- `Batch_InodeRef`: append a packed inode ref, or convert to `INODE_EXTREF` if it would exceed max item size and extended refs are enabled.
- `Batch_InodeExtRef`: append an extended inode ref.
- `Batch_DeleteDirItem`: remove one packed dir item, possibly replacing the item with a shorter inserted copy.
- `Batch_DeleteInodeRef`: remove one packed inode ref; if absent and extended refs are enabled, enqueue a matching extended-ref delete.
- `Batch_DeleteInodeExtRef`: remove one packed extended inode ref.
- `Batch_DeleteXattr`: remove one packed xattr by name.
- `Batch_Delete`: mark existing item deleted.

When an existing packed item is modified but not fully deleted, the function allocates a new shorter or longer data buffer, creates a replacement `tree_data`, marks the old item ignored, and updates tree item counts/sizes.

`add_delete_inode_extref` is a helper for the compatibility path where a requested inode-ref delete must be represented as an extended-ref delete.

## Batch Commit Flow

Inside `commit_batch_list_root`:

1. Find the tree position for the current batch key.
2. Determine the end key for the current leaf range with `find_tree_end`.
3. Handle range-delete operations specially:
   - `Batch_DeleteInode` marks all items with the target object id ignored.
   - `Batch_DeleteExtentData` marks all extent data items for an inode ignored.
   - `Batch_DeleteFreeSpace` marks free-space keys in a range ignored.
4. For normal operations, allocate a new `tree_data` unless it is a delete-only operation.
5. Insert into the current tree or call `handle_batch_collision`.
6. Consume subsequent batch items that fit before the current tree end key, applying them in-place without repeated root searches.
7. Update parent generations and revive ignored parent items.
8. Free consumed batch items at the end.

This design amortizes tree searches by applying adjacent sorted operations to the same loaded leaf when possible.

## Locking And Concurrency Assumptions

Many public functions are annotated or named for use under `Vcb->tree_lock`.

- `find_item` and traversal functions require the tree lock held.
- Insert, delete, and batch commit require the tree lock held exclusively.
- Tree load uses per-tree fast mutexes or root load locks to prevent duplicate child loads.
- Global tree cache insertion/removal uses `Vcb->trees_list_mutex`.
- Rollback space operations acquire chunk locks when updating per-chunk free-space accounting.

The file assumes callers obey lock ownership. It does not generally try to make tree mutation safe without the exclusive tree lock.

## Error Handling

The file returns `NTSTATUS` for operations that can fail and uses boolean returns for traversal convenience.

Common failures:

- Pool allocation failure.
- Invalid or oversized node item arrays.
- Overlarge item payloads.
- Read failure from disk.
- Unexpected duplicate key.
- Unsupported packed-item growth beyond node item limits.
- Malformed/truncated packed records.
- Missing tree paths.

The code logs errors but often leaves deeper recovery to the caller. Batch commit failures can occur after some in-memory mutations, which is why rollback support in surrounding write paths is important.

## Dependencies

Key dependencies from the wider driver:

- `btrfs_drv.h` for tree/root/item structures, batch operation enums, rollback structures, Btrfs item structs, locks, and helper prototypes.
- `crc32c.h` for tree address hash bucketing and extended ref key hashing.
- `read_data` for loading tree blocks.
- `keycmp` for Btrfs key ordering.
- `update_changed_extent_ref`, `get_chunk_from_address`, `space_list_add2`, `space_list_subtract2`, chunk locks, and inode/extent accounting helpers.
- Windows kernel allocation, lookaside lists, fast mutexes, resources, and list primitives.

## Risks And Review Notes

- Tree item data for loaded leaves points into the raw tree buffer; inserted or replacement item data has separate ownership. Correct use of `td->inserted` is critical for freeing.
- Lazy deletion through `ignore` makes traversal semantics subtle. Callers must choose ignore behavior intentionally.
- `find_prev_item` explicitly lacks ignore handling, which can matter for callers expecting visible-only reverse traversal.
- Several packed-item delete paths assume record walking remains within validated lengths; they mostly validate but should be fuzz-tested with malformed metadata.
- Batch collision logic performs many manual buffer reallocations and size recalculations; off-by-one errors here can corrupt tree state.
- The `Batch_InodeRef` overflow conversion to extended refs depends on incompat flags and sorted insertion into the remaining batch list.
- Batch commit applies multiple mutations before freeing the batch list; error paths should be reviewed together with caller rollback guarantees.
