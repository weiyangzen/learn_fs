# File Research: sources/local-fs/kdave-linux/fs/btrfs/ref-verify.c

## Purpose

`ref-verify.c` implements the debug-only Btrfs reference verifier. It builds and maintains an in-memory model of extent references and compares delayed-reference operations against expected reference state. On inconsistency it prints detailed block/ref/action history, disables `REF_VERIFY`, and frees the cache.

This file is compiled only when enabled through `ref-verify.h` under `CONFIG_BTRFS_DEBUG`, and runtime behavior is gated by the `REF_VERIFY` mount option.

## Core Model

The verifier stores block reference state in red-black trees.

`struct block_entry` tracks one referenced extent/block:

- `bytenr`
- `len`
- `num_refs`
- `metadata`
- `from_disk`
- `roots`: root reference counts for direct refs.
- `refs`: expected detailed references.
- `actions`: chronological ref actions with stack traces.
- `node`: rb-tree membership in `fs_info->block_tree`.

`struct ref_entry` models a reference expected in the extent tree:

- `root_objectid`
- `parent`
- `owner`
- `offset`
- `num_refs`

`struct root_entry` tracks direct reference counts per root for a block.

`struct ref_action` records a mutation:

- delayed-ref action type.
- real root that caused it.
- copied reference details.
- stack trace up to `MAX_TRACE`.

## Tree Helpers

The file defines rb-tree comparison/insert/lookup helpers for:

- block entries by `bytenr`.
- root entries by `root_objectid`.
- ref entries by `(root_objectid, parent, owner, offset)`.

`free_block_entry()` releases root entries, ref entries, action history, and the block entry itself.

`add_block_entry()` allocates or finds a block entry and optionally initializes a root entry.

## Building State From Disk

`btrfs_build_ref_tree()` walks the extent tree at mount time when `REF_VERIFY` is enabled. It locks and walks the tree manually using:

- `walk_down_tree()`
- `walk_up_tree()`
- `process_leaf()`
- `process_extent_item()`

It parses extent items and standalone ref items:

- `BTRFS_EXTENT_ITEM_KEY`
- `BTRFS_METADATA_ITEM_KEY`
- `BTRFS_TREE_BLOCK_REF_KEY`
- `BTRFS_SHARED_BLOCK_REF_KEY`
- `BTRFS_EXTENT_DATA_REF_KEY`
- `BTRFS_SHARED_DATA_REF_KEY`
- `BTRFS_EXTENT_OWNER_REF_KEY`

Handlers populate the in-memory model:

- `add_tree_block()` for tree block refs.
- `add_extent_data_ref()` for direct data refs.
- `add_shared_data_ref()` for shared data refs.

For `BTRFS_EXTENT_OWNER_REF_KEY`, the verifier accepts it only when simple quotas are enabled.

If the extent root is unavailable, the verifier warns and disables `REF_VERIFY`.

## Tracking Runtime Ref Modifications

`btrfs_ref_tree_mod()` is the main runtime entry point. It is called when a Btrfs delayed reference is added or dropped.

It converts `struct btrfs_ref` into the verifier’s `ref_entry` key fields:

- metadata refs use tree level as owner.
- non-shared data refs use objectid and file offset.
- parent refs represent shared refs.
- direct refs track roots.

It then records the action and updates the in-memory block/ref/root counters under `fs_info->ref_verify_lock`.

Important checked cases:

- Adding an extent to a block that still has references is reported as reallocation of a live block.
- Modifying a bytenr with no existing entry is an error.
- Dropping a ref from a block with zero total refs is an error.
- Dropping a non-existing detailed ref is an error.
- Adding a duplicate metadata tree-block ref is an error.
- Root reference counts are incremented/decremented for direct refs.

For `BTRFS_ADD_DELAYED_EXTENT`, it creates or reuses the block entry, increments total refs, marks metadata when relevant, and clears stale action history if the allocation is valid.

For `BTRFS_DROP_DELAYED_REF`, it decrements or removes matching `ref_entry` state and decrements block/root counts.

For `BTRFS_ADD_DELAYED_REF`, it increments existing data refs or adds new refs, and increments block/root counts.

On any verifier failure, it calls:

- `btrfs_free_ref_cache()`
- `btrfs_clear_opt(..., REF_VERIFY)`

This prevents cascading verifier noise after the first detected inconsistency.

## Diagnostics

`dump_block_entry()` prints block state, refs, root entries, and action history. `dump_ref_action()` prints action details and a stack trace.

Stack trace support is conditional on `CONFIG_STACKTRACE`:

- enabled: records with `stack_trace_save()` and prints with `stack_trace_print()`.
- disabled: prints a no-stacktrace-support message.

## Cache Freeing and Range Removal

`btrfs_free_ref_cache()` frees the entire verifier cache, but only if `REF_VERIFY` is active.

`btrfs_free_ref_tree_range()` removes cached block entries within a block-group range. It also detects and reports entries that overlap the range boundaries, which indicates inconsistent tracking around block group removal or extent lifetime.

## Concurrency

All verifier tree and counter mutations are protected by `fs_info->ref_verify_lock`. Long frees use `cond_resched_lock()` to avoid monopolizing CPU while holding the spinlock during teardown.

## Dependencies

The file depends on Btrfs extent tree accessors, delayed reference definitions, path/tree locking helpers, and filesystem mount options. It is a diagnostic integrity tool rather than production IO-path functionality.
