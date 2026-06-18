# File Research: sources/windows/winbtrfs/src/extent-tree.c

## Scope

This file implements WinBtrfs extent-tree reference manipulation and changed-extent staging. It covers Btrfs extent item creation, conversion from old extent formats, inline and non-inline backreference insertion/removal, refcount and uniqueness queries, extent flag reads/writes, and in-memory tracking of changed data extents before transaction flush.

The file is in subset A through `sources/windows/winbtrfs`.

## High-Level Role

`extent-tree.c` is the driver-side extent accounting layer for WinBtrfs. Its main responsibility is to keep the on-disk extent tree consistent when file data or tree blocks gain or lose references. It knows the Btrfs extent item encodings (`EXTENT_ITEM`, `EXTENT_ITEM_V0`, skinny metadata items, inline refs, and separate ref items) and provides the helpers used by higher-level write, COW, truncation, deletion, and flush paths.

Core responsibilities:
- Compute Btrfs extent-data-reference hashes.
- Build sorted extent-reference lists and serialize them as inline refs or separate ref tree items.
- Upgrade old `EXTENT_ITEM_V0` plus `TYPE_EXTENT_REF_V0` records into current extent items.
- Increase and decrease extent refcounts for data, tree blocks, shared data, shared tree blocks, and legacy refs.
- Delete checksum ranges when data extents become unreferenced and are not superseded.
- Query total extent refcounts, uniqueness, flags, and shared-ref counts.
- Maintain per-chunk `changed_extent` records with current and old extent-data refs for later commit processing.

## Main APIs And Entry Points

- `get_extent_data_ref_hash2(root, objid, offset)`: computes the Btrfs hash key for an `EXTENT_DATA_REF` from root, inode/object id, and logical offset.
- `increase_extent_refcount(...)`: central insertion/increment path for extent refs. It creates missing extent items, converts old items, increments inline refcounts, inserts new inline refs when size allows, or creates separate non-inline ref items.
- `increase_extent_refcount_data(...)`: data-ref convenience wrapper around `increase_extent_refcount`.
- `decrease_extent_refcount(...)`: central deletion/decrement path. It locates skinny or normal extent items, converts old items as needed, decrements inline or non-inline refs, deletes the whole extent item when the total refcount reaches zero, and removes checksums for dropped data extents.
- `decrease_extent_refcount_data(...)`: data-ref convenience wrapper around `decrease_extent_refcount`.
- `decrease_extent_refcount_tree(...)`: tree-block-ref convenience wrapper around `decrease_extent_refcount`.
- `get_extent_refcount(...)`: returns the stored total refcount from skinny metadata, normal extent items, or old extent items.
- `is_extent_unique(...)`: determines whether all refs for a data extent point at the same root/object/offset, allowing multi-count refs to still count as unique to one logical owner.
- `get_extent_flags(...)` and `update_extent_flags(...)`: read and mutate the `EXTENT_ITEM.flags` field.
- `update_changed_extent_ref(...)`: transaction-time staging API that updates or creates a `changed_extent` entry under the chunk's `changed_extents_lock`, preserving old refs and applying ref deltas.
- `add_changed_extent_ref(...)`: simpler changed-extent append/merge path without old-ref lookup or locking in this function.
- `find_extent_shared_tree_refcount(...)`: returns whether a shared tree block ref exists for a parent.
- `find_extent_shared_data_refcount(...)`: returns the count for a shared data ref by parent.

## Internal Helpers

- `extent_ref` is a local list node that stores one of `EXTENT_DATA_REF`, `SHARED_DATA_REF`, `TREE_BLOCK_REF`, or `SHARED_BLOCK_REF`, plus its type and sort hash.
- `get_extent_hash(type, data)` normalizes the key offset/hash for each supported ref type.
- `free_extent_refs`, `add_shared_data_extent_ref`, `add_shared_block_extent_ref`, and `add_tree_block_extent_ref` build temporary reference lists while converting old extents.
- `sort_extent_refs` insertion-sorts refs by type ascending and hash descending, matching the ordering expected by this implementation.
- `construct_extent_item(...)` serializes a newly constructed extent item, keeping as many refs inline as fit within one quarter of the node size and inserting the rest as separate ref items.
- `convert_old_extent(...)` deletes a legacy old-style extent item, scans following `TYPE_EXTENT_REF_V0` items, transforms them into current shared/tree refs, and reinserts a modern extent item.
- `find_extent_data_refcount(...)` searches inline refs first, then non-inline `TYPE_EXTENT_DATA_REF`, to discover the previous count for a specific data ref.
- `get_changed_extent_item(...)` finds or allocates a per-chunk `changed_extent`.

## Control Flow And Algorithms

Extent ref insertion starts by locating the expected extent-tree item. For missing items, `increase_extent_refcount` constructs a new `EXTENT_ITEM`, optionally appending `EXTENT_ITEM2` for non-skinny tree blocks, writes the first inline ref, and inserts either `TYPE_METADATA_ITEM` or `TYPE_EXTENT_ITEM`. Existing old-format items are first converted through `convert_old_extent`, after which the insertion retries against the modern format.

For existing modern extent items, insertion scans inline refs and handles matching refs in place by copying the extent item, increasing both the total `EXTENT_ITEM.refcount` and the matching section count where applicable, deleting the old tree item, and reinserting the updated copy. If no matching inline ref exists and all refs are still inline, the function inserts a new inline section when the item stays below the local max inline item size. Otherwise it searches or creates the appropriate non-inline ref item and updates the main extent item's total refcount.

Extent ref deletion mirrors that model. `decrease_extent_refcount` finds skinny metadata or normal extent items, validates size and refcount, scans inline sections, and either deletes the whole extent item when the requested removal consumes the total refcount or rewrites the item with a reduced or removed section. If inline refs do not account for the full total, it locates the non-inline ref item, reduces or deletes that item, then reduces or deletes the owning extent item. Data extent removal calls `add_checksum_entry(..., NULL, ...)` when the extent is no longer referenced and the removal is not superseded.

Old extent conversion reads a legacy `EXTENT_ITEM_V0`, deletes it, then walks following `TYPE_EXTENT_REF_V0` entries for the same address. Tree refs become top-level `TREE_BLOCK_REF` entries when the old ref's key offset equals the extent address, otherwise shared block refs. Data refs become shared data refs keyed by parent. The converted item is rebuilt by `construct_extent_item` with `EXTENT_ITEM_SHARED_BACKREFS`.

Uniqueness is stricter than a raw refcount test. `is_extent_unique` returns true immediately for refcount 1, but for higher counts it accepts only `TYPE_EXTENT_DATA_REF` refs and requires every inline and non-inline ref to share the same root, inode, and offset. Any shared refs, old-format items, malformed items, missing refs, or unaccounted refs make the function return false.

Changed-extent staging groups ref deltas by chunk, address, and size. `update_changed_extent_ref` initializes `ce->count` and `ce->old_count` from the current extent-tree item, records the old data ref count in `ce->old_refs` if one exists, records the new count in `ce->refs`, applies the signed delta, and marks the extent as superseded when requested. This gives later flush code enough state to reconcile data extent ref changes and checksum handling.

## Important State Mutated

- Extent tree items in `Vcb->extent_root`, including `TYPE_EXTENT_ITEM`, `TYPE_METADATA_ITEM`, `TYPE_EXTENT_DATA_REF`, `TYPE_SHARED_DATA_REF`, `TYPE_TREE_BLOCK_REF`, `TYPE_SHARED_BLOCK_REF`, and legacy `TYPE_EXTENT_REF_V0`.
- `EXTENT_ITEM.refcount`, `EXTENT_ITEM.generation`, and `EXTENT_ITEM.flags`.
- Inline ref records embedded after `EXTENT_ITEM` and optional `EXTENT_ITEM2`.
- Checksum tree ranges through `add_checksum_entry` when data extents are fully removed.
- Per-chunk `changed_extents`, each `changed_extent`'s `count`, `old_count`, `no_csum`, `superseded`, `refs`, and `old_refs`.

## Dependencies

This file depends heavily on project-local Btrfs tree helpers and definitions from `btrfs_drv.h`, including:
- `find_item`, `find_next_item`, `insert_tree_item`, `delete_tree_item`, and `keycmp`.
- `get_extent_data_len`, `get_extent_data_refcount`, `add_checksum_entry`.
- Btrfs structures and constants such as `EXTENT_ITEM`, `EXTENT_ITEM2`, `EXTENT_ITEM_V0`, `EXTENT_DATA_REF`, `SHARED_DATA_REF`, `TREE_BLOCK_REF`, `SHARED_BLOCK_REF`, `EXTENT_REF_V0`, `TYPE_EXTENT_ITEM`, `TYPE_METADATA_ITEM`, and `BTRFS_INCOMPAT_FLAGS_SKINNY_METADATA`.
- Runtime state structures such as `device_extension`, `chunk`, `changed_extent`, `changed_extent_ref`, `KEY`, and `traverse_ptr`.

Windows kernel dependencies include pool allocation/freeing (`ExAllocatePoolWithTag`, `ExFreePool`), list primitives (`LIST_ENTRY`, `InsertTailList`, `RemoveEntryList`, `IsListEmpty`), resource locking (`ExAcquireResourceExclusiveLite`, `ExReleaseResourceLite`), and memory copying (`RtlCopyMemory`).

## Notable Behaviors

- Inline refs are preferred while the extent item remains below a fraction of the Btrfs node size; larger ref sets spill into separate keyed ref items.
- The code supports skinny metadata for tree blocks by using `TYPE_METADATA_ITEM` keyed by level and omitting `EXTENT_ITEM2`.
- Some ref types are idempotent for increases: attempts to increase non-shared tree refs or shared block refs that already exist return success rather than increasing an embedded count.
- Shared data refs store a full `SHARED_DATA_REF` inline, but non-inline `TYPE_SHARED_DATA_REF` items store only a `uint32_t` count keyed by parent.
- `update_extent_flags` mutates the item data in place after locating the tree item, unlike most refcount paths that delete and reinsert copied items.
- Query helpers generally return `0` or `false` on malformed or missing items after logging, so callers must treat those values as failure-prone rather than authoritative absence in all contexts.

## Risks And Edge Cases

- Several allocation results are not consistently checked before use. In the inline insertion path, `newei = ExAllocatePoolWithTag(...)` is followed immediately by `RtlCopyMemory(newei, ...)` without a null check, unlike most neighboring allocations.
- Delete-then-reinsert update patterns can leave the extent tree partially changed if reinsertion fails after a successful deletion. The broader transaction/rollback layer has to recover from these intermediate states.
- Some allocated buffers are not freed on later failure paths because ownership is transferred only on successful `insert_tree_item`; if insertion fails, the local buffer can leak unless the callee takes ownership on failure.
- `decrease_extent_refcount_tree` passes `NULL` for `firstitem` with a FIXME. If an old tree extent must be converted in that path, conversion may lack accurate first-item metadata.
- `find_extent_shared_tree_refcount` and `find_extent_shared_data_refcount` contain FIXME comments for old-format extent handling; old extent items may yield incomplete shared-ref answers.
- `is_extent_unique` searches only normal `TYPE_EXTENT_ITEM` at `(address, size)` after `get_extent_refcount`; skinny metadata is not part of its positive path and old-format items are treated as non-unique.
- Hash collision handling for non-inline `TYPE_EXTENT_DATA_REF` and `TYPE_SHARED_DATA_REF` logs an internal error. The code detects collisions but does not have a collision-resolution scheme beyond failing.
- `add_changed_extent_ref` manipulates `changed_extents` without acquiring `changed_extents_lock` in this function, unlike `update_changed_extent_ref`; callers must provide synchronization if used concurrently.
- `update_extent_flags` returns `void` and only logs failures, so callers cannot tell whether a flag update actually landed.

## Cross-File Relationships

- `flushthread.c` calls the extent refcount and changed-extent helpers while committing dirty trees, data extents, chunks, and checksums.
- File write/truncate/delete paths depend on `increase_extent_refcount_data`, `decrease_extent_refcount_data`, and changed-extent staging to maintain data extent ownership.
- Metadata COW paths depend on `increase_extent_refcount` and `decrease_extent_refcount_tree` for tree block lifetime.
- Checksum maintenance is delegated to `add_checksum_entry`, which is implemented outside this file and is triggered here only when data extent references are fully dropped.

## Summary

`extent-tree.c` is the WinBtrfs extent-reference authority. It translates higher-level ownership changes into precise Btrfs extent-tree mutations, including old-format migration, skinny metadata support, inline/non-inline backref management, checksum invalidation for freed data extents, and per-chunk changed-extent bookkeeping. Its correctness is central to avoiding leaked extents, premature frees, corrupted backrefs, and incorrect copy-on-write decisions.
