# File Research: sources/os/linux/linux-stable/fs/btrfs/ref-verify.c

## Purpose

Implements the debug-only Btrfs reference verifier used when `REF_VERIFY` is enabled. It builds an in-memory model of extent references from the on-disk extent tree and then checks later delayed-reference mutations against that model.

The verifier is intended to catch reference accounting bugs, stale references, missing references, incorrect reallocation, and mismatches between expected and actual extent-tree state.

## In-Memory Model

The file defines four private structures:

- `root_entry`: direct reference count per root for a block.
- `ref_entry`: expected extent reference tuple: root, parent, owner, offset, count.
- `ref_action`: historical add/drop action with delayed-ref action code, root, ref tuple, list node, and optional stack trace.
- `block_entry`: one referenced extent/tree block, keyed by bytenr, with length, total refs, metadata flag, from-disk flag, root/ref rbtrees, and action history.

`fs_info->block_tree` stores `block_entry` records keyed by bytenr. Each block entry contains separate rbtrees for roots and refs.

## Rbtree Operations

The file provides comparison/lookup/insert helpers for:

- `block_entry` by bytenr.
- `root_entry` by root objectid.
- `ref_entry` by root, parent, owner, and offset.

Existing duplicate entries are returned so counts can be merged or errors detected.

## Stack Trace Support

When `CONFIG_STACKTRACE` is enabled:

- `__save_stack_trace()` records up to `MAX_TRACE` entries per ref action.
- `__print_stack_trace()` prints stored call stacks during diagnostics.

Without stacktrace support, diagnostics report that stacktrace support is unavailable.

## Building the Initial Ref Tree

Entry point: `btrfs_build_ref_tree()`.

At mount, if `REF_VERIFY` is enabled, it:

1. Gets the extent root.
2. Allocates a Btrfs path.
3. Locks the root node for read.
4. Walks the entire extent tree manually using `walk_down_tree()` and `walk_up_tree()`.
5. Processes each leaf with `process_leaf()`.

`process_leaf()` handles:

- `BTRFS_EXTENT_ITEM_KEY`
- `BTRFS_METADATA_ITEM_KEY`
- `BTRFS_TREE_BLOCK_REF_KEY`
- `BTRFS_SHARED_BLOCK_REF_KEY`
- `BTRFS_EXTENT_DATA_REF_KEY`
- `BTRFS_SHARED_DATA_REF_KEY`

`process_extent_item()` parses inline refs from extent items and delegates to:

- `add_tree_block()`
- `add_extent_data_ref()`
- `add_shared_data_ref()`

It tolerates `BTRFS_EXTENT_OWNER_REF_KEY` only when simple quotas are enabled.

## Reference Mutation Verification

Main mutation hook: `btrfs_ref_tree_mod()`.

It returns immediately unless `REF_VERIFY` is enabled.

For each delayed reference operation, it:

1. Converts `struct btrfs_ref` into a verifier `ref_entry`.
2. Allocates a `ref_action` and records the stack.
3. Handles `BTRFS_ADD_DELAYED_EXTENT` as a new allocation.
4. For add/drop refs, finds the existing block entry and validates counts.
5. Inserts, increments, decrements, or removes matching `ref_entry` records.
6. Updates root-level and block-level counts.
7. Appends the action to the block history.

Detected errors include:

- Adding an extent to a bytenr that still has references.
- Dropping a ref for a block with no entry.
- Dropping a ref from a block with zero total refs.
- Dropping a nonexistent ref tuple.
- Adding a second metadata ref to an existing tree-block ref.
- Missing expected root entries.

On error, it dumps detailed state and disables `REF_VERIFY` after freeing the cache.

## Diagnostics

`dump_block_entry()` prints:

- Block bytenr/len.
- Total refs.
- Metadata/from-disk flags.
- All ref entries.
- All root entries.
- Historical ref actions with stack traces.

`dump_ref_action()` prints the action and reference tuple associated with a mutation.

## Cache Cleanup

`btrfs_free_ref_cache()` frees the entire verifier tree under `ref_verify_lock`.

`btrfs_free_ref_tree_range()` removes cached block entries in a given physical range, warning if existing entries overlap the range boundaries. This is used when a range is freed or otherwise no longer valid for verifier tracking.

## Locking

The verifier uses `fs_info->ref_verify_lock` to protect the global `block_tree` and all nested state. Some helper functions intentionally return with the lock still held so callers can continue mutating the relevant block entry before unlocking.

## Failure Policy

The verifier is diagnostic. On internal inconsistency or build failure, it frees its cache and clears `REF_VERIFY` from mount options rather than continuing with a corrupted model.
