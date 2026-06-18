# File Research: sources/os/linux/linux-stable/fs/jffs2/erase.c

## Role

Manages eraseblock erase lifecycle: starting erases, handling success/failure, verifying erased contents, writing clean markers, freeing raw node refs, and moving blocks among JFFS2 erase lists.

## Erase Flow

- `jffs2_erase_pending_blocks()` processes one or more blocks from:
  - `erase_complete_list`, by verifying and marking erased blocks;
  - `erase_pending_list`, by clearing accounting/node refs and starting an MTD erase.
- `jffs2_erase_block()` issues `mtd_erase()` for Linux or platform flash erase for eCos.
- `jffs2_erase_succeeded()` moves the block to `erase_complete_list`, triggers GC, and wakes waiters.
- `jffs2_erase_failed()` optionally updates NAND bad-block handling, retries if appropriate, or moves the block to `bad_list`.

## Node Ref Cleanup

- `jffs2_free_jeb_node_refs()` frees all raw node refs for an eraseblock.
- `jffs2_remove_node_refs_from_ino_list()` removes refs from their owning inode/xattr raw-node chain and releases inode/xattr caches when appropriate.

## Erase Verification and Clean Marker

- `jffs2_block_check_erase()` verifies a freshly erased block is all `0xff`.
  - Uses `mtd_point()` when possible for direct mapped access.
  - Falls back to page-sized reads.
  - Returns bad offsets for failure reporting.
- `jffs2_mark_erased_block()`:
  - verifies erase;
  - writes NAND OOB cleanmarker, in-band cleanmarker, or no marker depending on medium setup;
  - accounts cleanmarker refs when in-band;
  - moves the block to `free_list` and updates free/erasing counters.

## Synchronization

- `erase_free_sem` coordinates erase-list transitions and prevents ref freeing races.
- `erase_completion_lock` protects list membership and accounting counters.
- Waiters use `erase_wait`.

## Research Notes

This file is where the physical flash erase lifecycle meets JFFS2’s logical accounting. It carefully transitions blocks between dirty/erasing/complete/free/bad states and verifies erased media before reuse.
