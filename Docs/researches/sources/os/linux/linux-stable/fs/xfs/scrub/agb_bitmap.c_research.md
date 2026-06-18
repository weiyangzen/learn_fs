# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/agb_bitmap.c

## Purpose

Implements scrub helpers for recording allocation-group block numbers in a typed bitmap, with special support for marking btree blocks seen during btree traversal.

## Main Functions

- `xagb_bitmap_set_btblocks`
  - Visits every block in a per-AG btree and marks each block in an AG block bitmap.
- `xagb_bitmap_set_btcur_path`
  - Records the current btree cursor path from leaf toward root, stopping when the cursor is no longer at the first record/key of a level.

## Algorithm Notes

`xagb_bitmap_set_btcur_path` relies on left-to-right btree traversal behavior:
- When the cursor pointer for a level is `1`, this is the first time traversal has entered that block.
- The helper records that block.
- Once a level pointer is not `1`, ancestors above it have already been seen for this traversal path.

## Important Invariants

- Only buffers returned by `xfs_btree_get_block` are recorded.
- Buffer disk addresses are converted to filesystem blocks and then AG block numbers.
- Bitmap insertion is delegated to `xagb_bitmap_set`.

## Dependencies

- Uses generic btree block visitation.
- Wraps scrub bitmap operations from `bitmap.h` through the typed `xagb_bitmap` interface.

## Research Notes

This file is a scrub utility for avoiding duplicate btree block accounting during scans. It depends on traversal order guarantees from the btree query path.
