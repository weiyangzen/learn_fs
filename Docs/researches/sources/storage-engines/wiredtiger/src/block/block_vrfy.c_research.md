# sources/storage-engines/wiredtiger/src/block/block_vrfy.c

## Purpose

`block_vrfy.c` verifies physical block-file layout against checkpoint metadata and B-tree traversal. It tracks allocation-size fragments in bitmaps to detect duplicate references, missing references, references beyond checkpoint/file size, and corrupted extent lists.

## Important APIs, Types, and Functions

Entry points are `__wt_block_verify_start`, `__wt_block_verify_end`, `__wti_verify_ckpt_load`, `__wti_verify_ckpt_unload`, and `__wt_block_verify_addr`. Private helpers include `__verify_last_avail`, `__verify_set_file_size`, `__verify_filefrag_add`, `__verify_filefrag_chk`, `__verify_ckptfrag_add`, and `__verify_ckptfrag_chk`. Macros `WT_wt_off_TO_FRAG` and `WT_FRAG_TO_OFF` translate between file offsets and bitmap positions, excluding the descriptor block.

## Control Flow

Verify start parses `strict`, `dump_layout`, and `dump_tree_shape`, selects the last real checkpoint, sets `block->size` to that checkpoint's durable file size, validates allocation-size alignment, allocates the per-file fragment bitmap, marks the handle as verifying, initializes `verify_alloc`, and loads the last checkpoint's available list into the file-fragment bitmap.

For each checkpoint load, verification records root/extent-list blocks as seen, merges checkpoint allocation extents into accumulated `verify_alloc`, removes discard extents, reads available extents for corruption checking, removes the checkpoint root from accumulated allocation, then builds a per-checkpoint bitmap of expected blocks. During B-tree verification, `__wt_block_verify_addr` marks file fragments and clears checkpoint fragments. Checkpoint unload and verify end report any remaining expected or missing ranges.

## State and Persistence Behavior

Verification is read-only for disk content but mutates `WT_BLOCK` verification state: `verify`, `verify_strict`, `verify_layout`, `dump_tree_shape`, `verify_size`, `frags`, `fragfile`, `fragckpt`, and `verify_alloc`. It intentionally overrides `block->size` to the last checkpoint's file size so references beyond the checkpoint fail even if the physical file has grown.

## Dependencies and Integration Points

The file integrates with checkpoint unpacking/loading, extent-list reads and merges, B-tree verify traversal, block read corruption behavior, verbose layout dumping, and bitmap helpers. It depends on `block_ext.c` to avoid panics during verification via `block->verify`.

## Risks and Edge Cases

Bitmap size scales with file size divided by allocation size; very large files with small allocation units can consume significant memory. Missing trailing fragments are tolerated because files may have been extended or truncated after the checkpoint; missing interior fragments are errors or warnings depending on strict mode. Duplicate checks differ between per-file and per-checkpoint maps because blocks can appear in multiple checkpoints but not multiple times in one checkpoint.

## Test Signals

Tests should cover strict versus non-strict missing-fragment behavior, duplicate references within one checkpoint, last-checkpoint available-list validation, corrupted extent lists returning verify errors rather than panics, references beyond checkpoint/file size, and `dump_layout` verbose output.
