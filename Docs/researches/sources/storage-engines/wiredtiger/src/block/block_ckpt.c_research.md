# sources/storage-engines/wiredtiger/src/block/block_ckpt.c

## Purpose
This file owns block-manager checkpoint lifecycle: loading/unloading checkpoint extent state, writing new checkpoint cookies, deleting and merging old checkpoint extent lists, maintaining incremental-backup block-modification bitmaps, and resolving checkpoint completion.

## Important APIs, Types, and Functions
Entry points include `__wti_block_ckpt_init`, `__wti_block_ckpt_destroy`, `__wt_block_checkpoint_load`, `__wt_block_checkpoint_unload`, `__wt_block_checkpoint_start`, `__wt_block_checkpoint`, `__wt_block_checkpoint_resolve`, and `__wti_block_checkpoint_extlist_dump`. Major helpers are `__ckpt_process`, `__ckpt_validate_state`, `__ckpt_read_deletion_extlists`, `__ckpt_delete_and_merge`, `__ckpt_update_live`, `__ckpt_update`, and bitmap helpers.

## Control Flow
Loading initializes checkpoint structures, unpacks cookies, returns root addresses, reads the live avail list, and truncates writable files to checkpoint size. Checkpoint creation starts by changing state to `WT_CKPT_INPROGRESS`, writes the root page if present, switches to first-fit allocation, and processes checkpoint entries. Processing validates state, enters a panic-on-failure window, reads deletion extent lists, records backup bits, merges deleted checkpoints, rewrites affected checkpoint cookies, updates the live checkpoint, and leaves newly reusable blocks in `ckpt_avail` until resolve.

Resolve runs after upper layers persist checkpoint metadata. Success merges `ckpt_avail` into live avail and frees temporary lists; failure after the fatal point panics and marks the block manager readonly.

## State and Persistence Behavior
Checkpoint cookies persist root addresses, extent-list addresses, file size, and checkpoint size. Live state includes alloc, avail, discard, and checkpoint-temporary extent lists. The two-phase protocol prevents reuse of freed checkpoint blocks until new checkpoint locations are durable. Incremental backup bitmaps track modified block ranges.

## Dependencies and Integration Points
The file depends on block extent-list APIs, allocation/free/write/truncate, metadata checkpoint-list conversion, verify hooks, spin locks, diagnostic flags, stats, and backup structures. It connects btree checkpoint logic with block allocation.

## Risks and Edge Cases
The fatal section cannot roll back merged extent lists. Tiered/non-local checkpoint handling must skip irrelevant extent lists. Intermediate checkpoint rewrite has a documented file-size limitation. Correct `live_lock` ownership is essential. Bitmap range clearing deliberately clears only full granularity units.

## Test Signals
Tests should cover live and readonly load/unload, empty roots, checkpoint deletion/merge chains, fake entries, tiered skips, resolve success/failure, backup bitmap set/clear, diagnostic overlap checks, and injected failures in the fatal checkpoint window.
