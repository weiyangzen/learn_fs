# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/bmap.c

## Purpose
Scrubs inode fork block mappings for data, attr, and CoW forks. It validates fork format, bmbt structure, incore extent records, physical target ranges, reverse mappings, realtime mappings, shared/CoW ownership, and special zapped-fork recovery signals.

## Main Entry Points
- `xchk_setup_inode_bmap`: obtains/locks inode, waits for DIO, flushes dirty data, invalidates page cache for repair, allocates scrub transaction, attaches dquots, and takes ILOCK.
- `xchk_bmap_data`
- `xchk_bmap_attr`
- `xchk_bmap_cow`

## Key Behavior
For btree-format forks, `xchk_bmap_btree` loads incore extents, checks btree blocks through generic btree scrub, verifies btree block owner fields on crc filesystems, and compares ondisk bmbt records to the incore extent tree unless the scrubber just loaded it.

The incore extent walk merges physically and logically contiguous mappings to reduce xref work. Each mapping is checked for order, logical range validity, dir/attr `xfs_dablk_t` addressability, physical data or realtime extent validity, and attr-fork prohibition on unwritten extents. Delalloc reservations are validated separately without disk xrefs.

Data/attr mappings are cross-referenced against rmapbt records with correct owner, offset, attr flag, unwritten flag, and non-bmbt flag. CoW fork mappings are checked against `XFS_RMAP_OWN_COW` and refcount CoW staging. Realtime mappings use rtgroup locking and rtrmap/refcount/bitmap helpers when available.

For apparently empty zapped data or attr forks, the scrubber can scan all AG or rtgroup reverse maps to detect rmaps that should have corresponding bmbt entries. This prevents a repaired-to-empty fork from being considered clean if rmaps still exist.

## Dependencies and Interactions
Uses inode locking, file writeback, bmbt, rmapbt/rtrmapbt, refcount, realtime group, health, and generic scrub btree helpers. Paired with `bmap_repair.c`.

## Failure Handling
Writeback `-ENOSPC` and `-EIO` do not stop metadata scrub. Broken xref trees are isolated through scrub xref processing. Zapped fork health flags are cleared only when scrub completes cleanly.
