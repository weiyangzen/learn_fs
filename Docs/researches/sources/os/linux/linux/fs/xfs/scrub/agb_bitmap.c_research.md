# File Research: sources/os/linux/linux/fs/xfs/scrub/agb_bitmap.c

## Purpose

`scrub/agb_bitmap.c` implements helpers for recording allocation-group block numbers of btree blocks into a type-safe scrub bitmap.

## Main Content

- Provides a btree block visitor that:
  - Retrieves the btree block buffer at a cursor level.
  - Converts buffer disk address to filesystem block.
  - Converts filesystem block to AG block.
  - Sets that AG block in an `xagb_bitmap`.
- Provides `xagb_bitmap_set_btblocks` to mark every block in a per-AG btree by using `xfs_btree_visit_blocks`.
- Provides `xagb_bitmap_set_btcur_path` to mark the current cursor path from leaf toward root while walking records.

## Key Interfaces and Invariants

- `xagb_bitmap_set_btcur_path` relies on btree query order from left edge to right edge.
- While walking records, a level’s block is newly seen when the cursor pointer at that level is `1`; once a non-first pointer is observed, higher levels have already been recorded for that path.
- The helpers record block numbers in AG block units, not fsblock units.
- Missing buffers during visitation are ignored.

## Dependencies

Depends on scrub bitmap wrappers, `xbitmap32`, generic btree cursor/block visitation, buffer disk addresses, and XFS block address conversion macros.
