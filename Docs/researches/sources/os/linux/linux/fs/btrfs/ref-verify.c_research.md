# File Research: sources/os/linux/linux/fs/btrfs/ref-verify.c

## Scope

`ref-verify.c` implements the debug-only Btrfs reference verifier. It builds an in-memory model of extent references from the extent tree at mount, updates that model when delayed refs are added or dropped, records action history with optional stack traces, and disables reference verification if an invariant fails.

## Data Structures

- `root_entry`: tracks direct reference counts per root for one block.
- `ref_entry`: models one expected extent reference keyed by root, parent, owner, and offset.
- `ref_action`: records a delayed-ref action, root, reference snapshot, list node, and stack trace.
- `block_entry`: models one referenced bytenr, its length, total refs, metadata/data classification, from-disk status, root/ref rbtrees, and action history.

All block entries live in `fs_info->block_tree` and are protected by `fs_info->ref_verify_lock`.

## Mount-Time Tree Build

`btrfs_build_ref_tree()` walks the extent root under read locks and populates the verifier tree. It processes:

- `BTRFS_EXTENT_ITEM_KEY`
- `BTRFS_METADATA_ITEM_KEY`
- `BTRFS_TREE_BLOCK_REF_KEY`
- `BTRFS_SHARED_BLOCK_REF_KEY`
- `BTRFS_EXTENT_DATA_REF_KEY`
- `BTRFS_SHARED_DATA_REF_KEY`
- `BTRFS_EXTENT_OWNER_REF_KEY` validation for simple quotas

Inline and keyed refs are normalized into `ref_entry` records. Metadata tree blocks are tracked with level information, and data refs are tracked by root, owner objectid, and offset.

If the extent root is unavailable or verification fails, the mount option is cleared and the cache is freed.

## Runtime Ref Updates

`btrfs_ref_tree_mod()` updates the verifier for delayed-ref operations when `REF_VERIFY` is enabled.

For `BTRFS_ADD_DELAYED_EXTENT`, it creates or reuses a block entry, increments total refs, marks metadata if appropriate, and checks that the allocation is not reusing a block that still has references.

For `BTRFS_ADD_DELAYED_REF`, it inserts or increments a matching `ref_entry`, increments total/root refs, and rejects duplicate metadata refs.

For `BTRFS_DROP_DELAYED_REF`, it decrements or removes a matching `ref_entry`, decrements total/root refs, and reports attempts to drop nonexistent refs or refs from zero-ref blocks.

Every successful update appends a `ref_action` with the delayed-ref action and stack trace.

## Cleanup APIs

`btrfs_free_ref_cache()` releases the entire verifier tree at unmount or after fatal verifier errors.

`btrfs_free_ref_tree_range()` removes verifier entries for a block-group range and reports block entries that overlap the range boundaries.

## Diagnostics

`dump_block_entry()` logs a block’s refs, roots, and action history. `dump_ref_action()` logs action fields and prints a stack trace when `CONFIG_STACKTRACE` is available.

Error paths dump the relevant model state, free the verifier cache, and clear `REF_VERIFY` to avoid continued use of a corrupted debug model.

## Dependencies

The file depends on Btrfs extent-tree formats, delayed-ref action constants, path/tree read locking, accessors, rbtrees, spinlocks, stacktrace support, and filesystem mount options.

## Risks And Invariants

- The verifier assumes all updates happen under `ref_verify_lock`.
- Metadata blocks may not gain duplicate matching refs.
- Total block refs and per-root refs must never underflow or disagree with actions.
- Shared refs and direct refs are keyed differently; confusing parent-vs-root refs would produce false verifier failures.
- The build walk must preserve current bytenr/length across extent items and separate ref-key items.

## Testing Signals

Relevant coverage includes enabling `ref_verify` on mount, loading trees with inline and external refs, shared data/block refs, metadata item refs, delayed ref add/drop sequences, reallocation after free, block-group removal, simple-quota owner refs, and stacktrace-enabled diagnostics.
