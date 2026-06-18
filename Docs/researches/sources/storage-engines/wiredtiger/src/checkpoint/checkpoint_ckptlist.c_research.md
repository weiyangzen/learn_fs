# sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_ckptlist.c

## Purpose

Owns cleanup of checkpoint-list memory. It frees arrays of `WT_CKPT` descriptors, clears saved btree checkpoint lists, and frees all heap-owned fields inside an individual checkpoint descriptor so the object can be reused or discarded safely.

## Important APIs, Types, And Functions

`__wt_ckptlist_free` frees a NULL-terminated checkpoint array using `WTI_CKPT_FOREACH_NAME_OR_ORDER`, which includes entries that may not yet have a name but do have an order. `__wt_ckptlist_saved_free` frees `S2BT(session)->ckpt` and resets `btree->ckpt_bytes_allocated`. `__wt_checkpoint_free` releases one `WT_CKPT`, including strings, buffers, block-manager private pointer, and incremental backup block-modification entries.

The code manipulates `WT_CKPT`, `WT_CKPT_BLOCK_MODS`, `WT_BTREE::ckpt`, and `WT_BLKINCR_MAX` block-mod slots.

## Control Flow

The list-free path returns immediately for a NULL base pointer. Otherwise it iterates every name-or-order entry, calls the single-checkpoint free helper, and frees the array pointer. The saved-list helper delegates to the generic list free routine and resets btree allocation accounting. The single-checkpoint free routine handles NULL input, frees all scalar-owned allocations, loops over every incremental backup block-mod entry to free bitstrings and IDs and clear validity, then `WT_CLEAR`s the whole descriptor.

## State And Persistence Behavior

This file only frees in-memory representations of checkpoint metadata that was read from or prepared for persistent metadata. It does not update metadata itself. Clearing `WT_CKPT` prevents stale checkpoint names, cookies, block metadata, or backup bitstrings from being reused after free. Resetting `ckpt_bytes_allocated` keeps btree memory accounting aligned after saved checkpoint lists are discarded.

## Dependencies And Integration Points

Used by checkpoint metadata parsing, btree handle cleanup, checkpoint close/reopen paths, and error handling that abandons checkpoint arrays. It depends on memory/buffer helpers and on the private iterator macro to handle not-yet-named checkpoints created during checkpoint assembly.

## Risks

Using the public `WT_CKPT_FOREACH` here would leak unnamed ordered checkpoints. Missing any owned field in `__wt_checkpoint_free` would leak memory or retain stale incremental-backup state. Clearing the descriptor after free is useful for reuse but means callers must not expect any field to survive. Destroying `bpriv` here assumes the block-manager private object is heap-owned by the checkpoint descriptor.

## Test Signals

Memory sanitizer/ASAN leak checks around checkpoint metadata load/drop, named checkpoint creation/drop, incremental backup metadata, and failed checkpoint assembly are the best signals. Unit tests should include a checkpoint list with an ordered but unnamed entry to verify the private iterator path.
