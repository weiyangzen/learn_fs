# sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_size.c

## Purpose
Maintains byte-size accounting for disaggregated block handles, including ordinary write/discard deltas, obsolete delta-chain removal, root-page size transitions during checkpoint, and rollback of checkpoint root-size accounting.

## Important APIs, types, and functions
- `__wti_block_disagg_get_size`, `__wti_block_disagg_increase_size`, and `__wti_block_disagg_decrease_size` are low-level atomic size operations on `WT_BLOCK_DISAGG`.
- `__wt_block_disagg_get_size`, `__wt_block_disagg_set_size`, and `__wt_block_disagg_obsolete_delta_chain` are btree/session-level wrappers for disaggregated trees.
- `__wti_block_disagg_apply_root_size` handles checkpoint root size replacement.
- `__wt_block_disagg_checkpoint_rollback` reverts root-size accounting if the current checkpoint generation fails.

## Control flow
Writes call increase; non-root discards and obsolete delta-chain notifications call decrease. Decrease saturates at zero if asked to subtract more than the current total. Checkpoint root handling saves the previous root size, records the new root size and checkpoint generation, subtracts the previous root, and adds the new root. Rollback checks that the btree is disaggregated and that the root-size generation matches the current checkpoint generation, then subtracts the current root and restores the previous root.

## State and persistence behavior
`WT_BLOCK_DISAGG::size` is an atomic live byte count used when checkpoint metadata records `WT_CKPT::size`. Root pages are special because old root discard occurs after checkpoint size is written; root transitions are accounted when the checkpoint is packed rather than when the old root is discarded. `current_root_size`, `previous_root_size`, and `root_size_gen` are transient block-handle state used to make failed checkpoints reversible.

## Dependencies and integration points
This file integrates with checkpoint packing in `block_disagg_ckpt.c`, page discard and write logic in `block_disagg_write.c`, delta-chain obsolete notifications from reconciliation, btree flags, and checkpoint generation tracking through `__wt_gen(session, WT_GEN_CHECKPOINT)`.

## Risks and edge cases
- There is an explicit FIXME for a disaggregated block size accounting bug; decrease currently saturates at zero instead of asserting.
- Size is updated atomically but root-size fields are not independently synchronized here; callers rely on checkpoint sequencing.
- Rollback only applies to the matching checkpoint generation, so generation mismanagement can leave wrong root-size accounting.
- Root pages are deliberately skipped by discard accounting; double subtraction would break verify/checkpoint size consistency.

## Test signals
Tests should validate write increments, discard decrements, saturation behavior for over-decrement, obsolete delta-chain size removal, root size replacement across checkpoints, rollback of failed checkpoints, no-op rollback on non-disaggregated btrees, and checkpoint metadata size matching live size after root transitions.
