# File Research: sources/local-fs/xfsprogs/db/fsmap.c

## Purpose
Implements the `fsmap` command, which displays physical block ownership records from data-device or realtime reverse-mapping btrees.

## Main Interfaces
- Registers `fsmap` through `fsmap_init()`.
- `fsmap_f()` accepts `[-r] [start_fsb] [end_fsb]`; `-r` selects realtime mapping.
- `fsmap_fn()` and `fsmap_rt_fn()` print rmap records with AG/rtgroup, start block, length, owner, offset, and flags.

## Control Flow
The data-device path bounds the requested range to filesystem size, converts start/end FSBs to AG ranges, opens each AGF, creates an rmapbt cursor, and calls `libxfs_rmap_query_range`. The realtime path builds equivalent range records in rtgroup coordinates, loads the realtime metadata directory and rtgroup rmap inode in an empty transaction, creates an rtrmap cursor, and queries the range.

## Dependencies
Requires `xfs_has_rmapbt(mp)`, libxfs rmap btree query APIs, per-AG iteration, rtgroup iteration, and rtgroup metadata inode loading.

## Risks And Invariants
- The command refuses filesystems without reverse-mapping btrees.
- Data-device range validation uses `sb_dblocks`; realtime range handling later clamps to `sb_rblocks`.
- Cursor, buffer, perag, rtgroup, and transaction lifetimes are explicitly released on all normal error paths.
