# File Research: sources/windows/reactos/drivers/filesystems/btrfs/extent-tree.c

## Purpose

Implements Btrfs extent-tree reference accounting for the ReactOS/WinBtrfs filesystem driver. This file is responsible for creating, converting, increasing, decreasing, querying, and staging extent references for both data extents and metadata tree blocks.

It handles Btrfs extent item formats including old `EXTENT_ITEM_V0`, modern `EXTENT_ITEM`, tree-block `EXTENT_ITEM2`, skinny metadata `TYPE_METADATA_ITEM`, inline reference records, and separate non-inline reference items.

## Main Responsibilities

- Compute Btrfs extent-data-ref hashes via CRC32C-derived `get_extent_data_ref_hash2`.
- Build sorted extent reference lists for `TYPE_EXTENT_DATA_REF`, `TYPE_SHARED_DATA_REF`, `TYPE_TREE_BLOCK_REF`, and `TYPE_SHARED_BLOCK_REF`.
- Construct modern `EXTENT_ITEM` records, using inline refs until item-size limits require non-inline ref tree items.
- Convert old-style extent items and `TYPE_EXTENT_REF_V0` records into newer extent-reference layouts.
- Increase and decrease extent refcounts for data and tree extents.
- Delete extent items when refcounts drop to zero and optionally re-add checksum entries when data extents are freed.
- Query extent refcount, flags, uniqueness, and shared-reference counts.
- Maintain per-chunk `changed_extent` lists used by write/flush paths to batch pending data-reference changes.

## Key Functions

- `get_extent_data_ref_hash2`: Computes the Btrfs hash key for an extent data reference from root, object id, and offset.
- `get_extent_hash`: Maps each extent ref type to the offset/hash key used in the extent tree.
- `construct_extent_item`: Builds and inserts an `EXTENT_ITEM`, optionally with `EXTENT_ITEM2`, inline refs, and overflow non-inline ref items.
- `convert_old_extent`: Deletes old `EXTENT_ITEM_V0`/`EXTENT_REF_V0` layout records and recreates modern extent refs.
- `increase_extent_refcount`: Adds or increments a reference, either inline in the extent item or as a separate extent-tree item.
- `decrease_extent_refcount`: Removes or decrements inline/non-inline refs, updates the containing `EXTENT_ITEM` refcount, and deletes items when fully unreferenced.
- `increase_extent_refcount_data` / `decrease_extent_refcount_data`: Convenience wrappers for `TYPE_EXTENT_DATA_REF`.
- `decrease_extent_refcount_tree`: Convenience wrapper for `TYPE_TREE_BLOCK_REF`.
- `find_extent_data_refcount`: Finds the current count for a specific data ref, checking inline refs first, then non-inline refs.
- `get_extent_refcount`: Returns the total recorded refcount for an extent, including old and skinny metadata formats.
- `is_extent_unique`: Determines whether all refs for an extent refer to a single root/inode/offset tuple.
- `get_extent_flags` / `update_extent_flags`: Read and mutate `EXTENT_ITEM.flags`.
- `update_changed_extent_ref`: Thread-safe update path for a chunk’s staged changed-extent list.
- `add_changed_extent_ref`: Adds a new staged changed extent ref when no old-disk lookup is needed.
- `find_extent_shared_tree_refcount`: Checks for a shared block ref from a parent tree block.
- `find_extent_shared_data_refcount`: Returns the count for a shared data ref from a parent.

## Data Structures

- Local `extent_ref` is an in-memory wrapper around one of the four extent-ref payload structs plus computed hash and list linkage.
- `changed_extent` and `changed_extent_ref` are maintained on `chunk.changed_extents`, protected by `chunk.changed_extents_lock` in the update path.
- Persistent on-disk items manipulated here include `EXTENT_ITEM`, `EXTENT_ITEM2`, `EXTENT_ITEM_V0`, `EXTENT_DATA_REF`, `SHARED_DATA_REF`, `TREE_BLOCK_REF`, and `SHARED_BLOCK_REF`.

## Important Behavior

- Inline refs are preferred until the item would exceed a fraction of the node size, then remaining refs are emitted as separate extent-tree items.
- Reference ordering follows Btrfs behavior: sorted forward by ref type, then descending by hash within a type.
- For tree blocks, skinny metadata support changes the key type from `TYPE_EXTENT_ITEM` to `TYPE_METADATA_ITEM` and uses the level as the key offset.
- Old-format extent conversion is lazy: increase/decrease paths detect `EXTENT_ITEM_V0`, convert it, then retry the operation.
- Data refs and shared data refs carry counts; tree block refs and shared block refs are treated as unit references.
- When a data extent’s last ref is removed and the removal is not marked `superseded`, the code calls `add_checksum_entry` with `NULL` to remove/stage checksum state for the freed range.

## Cross-File Interactions

- Declared in `btrfs_drv.h` and used by write, flush, clone, balance, fsctl, and tree mutation paths.
- Relies on `find_item`, `find_next_item`, `insert_tree_item`, and `delete_tree_item` from tree functions; those routines expect the VCB tree lock discipline documented in their annotations.
- `flushthread.c` consumes the `changed_extent` staging records and later applies refcount deltas with `increase_extent_refcount_data` and `decrease_extent_refcount_data`.
- `write.c`, `fileinfo.c`, `treefuncs.c`, `compress.c`, and `fsctl.c` stage changed references through `update_changed_extent_ref` or `add_changed_extent_ref`.

## Edge Cases and Risks

- The file performs many delete-then-insert updates; callers need the proper exclusive tree lock and error handling because partial update failures can leave metadata changed.
- Some paths depend on hash collision checks for non-inline data refs and return internal errors when a hash key resolves to a different ref tuple.
- Inline extent parsing is defensive about item sizes and unknown ref types, returning errors rather than trusting malformed metadata.
- `increase_extent_refcount` has a path that allocates a larger inline `EXTENT_ITEM` and immediately copies into it; unlike most allocation sites in this file, that allocation is not checked before use.
- `update_extent_flags` mutates item data in place after lookup, unlike most refcount updates that delete and reinsert items.
- `decrease_extent_refcount_tree` passes `NULL` for `firstitem` with a `FIXME`, which matters if old-format conversion needs complete tree block metadata.

## Research Summary

This is the core Btrfs extent reference accounting implementation for the ReactOS driver. It bridges compatibility with old on-disk extent formats, modern inline and non-inline reference items, and skinny metadata. It is central to copy-on-write correctness: incorrect behavior here would affect clone, write, flush, balance, checksum cleanup, and tree block lifetime management.
