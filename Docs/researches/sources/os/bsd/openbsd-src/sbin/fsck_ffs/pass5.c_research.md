# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass5.c

## Scope

Phase 5 for `fsck_ffs`: rebuilds cylinder-group summary information, inode/free-block bitmaps, fragment summaries, cluster summaries, and total free-count state from fsck’s computed inode/block maps.

## Main APIs

- `pass5()` is the only function. It constructs a fresh cylinder group image in `newcg`, compares it with each on-disk cylinder group, and repairs mismatches.

## Control Flow

The pass first handles conversion-level cluster-map creation/deletion when `cvtlevel >= 3`. It supports both `FS_42POSTBLFMT` and `FS_DYNAMICPOSTBLFMT`, calculating offsets for inode maps, block maps, and cluster summaries.

For each cylinder group, it initializes metadata fields, validates magic, recalculates inode usage from `inostathead`, marks pre-root inodes used in cg 0, then scans `blockmap` to rebuild free fragment/block maps and free counters. It updates fragment summaries via `ffs_fragacct()` and cluster run summaries when enabled. Per-cg summaries are accumulated into `cstotal`, compared to superblock summary slots, and repaired through `dofix()`.

At the end, the total superblock summary is compared and corrected, and `fs_ronly`/`fs_fmod` are cleared before marking the superblock dirty.

## Dependencies

- Uses FFS layout macros and bitmap helpers from `<ufs/ffs/fs.h>`.
- Consumes `blockmap` and `inostathead` built by prior phases.
- Uses `cglookup()`, `dirty()`, `sbdirty()`, `dofix()`.

## Risks And Edge Cases

- Old 4.2 rotational table format temporarily rewrites `fs_nrpos` to 8 and restores it after processing.
- Cluster-summary sizing can require superblock and cylinder-group layout changes.
- The repair messages are coarse-grained; bitmap mismatches are repaired by copying the computed map wholesale.
