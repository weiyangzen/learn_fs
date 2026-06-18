# File Research: sources/local-fs/xfsprogs/repair/bulkload.c

## Purpose

`bulkload.c` provides common reservation and cleanup support for rebuilding XFS btrees in repair. It tracks extents reserved for a new btree, hands blocks to the generic libxfs bulk-loader, frees unused reservations, and estimates btree slack under low-space conditions.

## Main Concepts

A `struct bulkload` owns a list of `bulkload_resv` records. Each reservation records a per-AG reference, starting AG block, length, and number of blocks already consumed. The bulk-loader consumes blocks one at a time through `bulkload_claim_block`.

## Main Functions

- `bulkload_init_ag` initializes state for AG-rooted btree rebuilds.
- `bulkload_init_inode` initializes state for inode-fork btree rebuilds and creates a fake ifork.
- `bulkload_add_extent` adds caller-designated blocks to the reservation list.
- `bulkload_alloc_file_blocks` allocates new blocks for file/inode-rooted btrees.
- `bulkload_claim_block` returns the next reserved block as a btree pointer.
- `bulkload_commit` frees unused reservation space after successful commit.
- `bulkload_cancel` frees all reserved space after failed rebuild.
- `bulkload_estimate_ag_slack` and `bulkload_estimate_inode_slack` tune bulk-load slack.

## Allocation and Cleanup Flow

`bulkload_alloc_file_blocks` repeatedly allocates extents starting near `alloc_hint`, validates the hint against EOFS, adds reservations, advances the hint, and finishes deferred operations. Cleanup uses `libxfs_free_extent_later` to free unused blocks and rolls deferred frees after `XREP_MAX_ITRUNCATE_EFIS` extents.

For committed btrees, used blocks remain allocated and only unused tails are freed. For cancelled rebuilds, every reserved block is freed.

## Important Invariants

- Reservation list entries hold passive per-AG references that must be released.
- `bulkload_claim_block` assumes the first list item still has space unless all space is exhausted.
- Used-up reservations are moved to the tail.
- Long-pointer btrees receive filesystem block pointers; short-pointer btrees receive AG block pointers.
- Inode bulk-load contexts must free the temporary fake ifork.

## Repair and Risk Notes

This file is shared infrastructure for rebuild paths. The important failure mode is incomplete cleanup after ENOSPC or transaction errors. The code tries to free disk reservations even on failure and then always frees incore reservation records.
