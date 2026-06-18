# File Research: sources/local-fs/reiserfsprogs/resize_reiserfs/do_shrink.c

Offline shrink implementation for `resize_reiserfs`. It moves all formatted and unformatted blocks above the new size boundary into free blocks below the boundary, updates references, shrinks bitmaps, and rewrites superblock accounting.

Major responsibilities:
- Tracks processed/moved internal, leaf, unformatted, and total block counts.
- `quit_resizer()` closes the filesystem and exits with the filesystem left in error state.
- `move_generic_block()` copies a block above the shrink boundary into a free block below it and updates the in-memory bitmap.
- `move_unformatted_block()` wraps generic movement for file data blocks.
- `move_formatted_block()` recursively walks internal/leaf tree blocks and rewrites child pointers and indirect item block pointers.
- `shrink_fs()` coordinates shrink feasibility checks, user confirmation, bitmap opening, FS error-state marking, root movement, bad-block list trimming, bitmap shrinking, and superblock updates.

Important implementation details:
- Shrink refuses when allocated blocks cannot fit after accounting for changed bitmap block count.
- The shrinker prints a beta warning and requires interactive confirmation.
- Before moving, it marks the filesystem state as `FS_ERROR` and writes the superblock so interruption forces fsck.
- Bad-block pseudo-file items are skipped during leaf indirect-pointer relocation, then collected and rewritten after bitmap shrink.
- Superblock free block count is adjusted by removed blocks, bitmap-block delta, and removed bad-block count.

Dependencies and interactions:
- Uses the shared buffer cache, bitmap, bad-block, tree item, and superblock helpers from `reiserfscore`.
- Called by `resize_reiserfs.c` when the target block count is smaller than the current filesystem.
- Relies on `opt_verbose` and other resize globals declared in `resize.h`.

Risks and notes:
- The shrink path is explicitly marked beta and dangerous.
- It recursively descends the full tree, so corrupt child pointers or malformed nodes can abort or miscount.
- `move_generic_block()` treats block number greater than block count as invalid, but equality handling should be checked against valid block range conventions.
- If no free block below the boundary is found, the tool exits and leaves the filesystem needing `reiserfsck`.
