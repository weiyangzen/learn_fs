# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dir_repair.c

## Role

Repairs corrupted XFS directories by constructing a replacement directory in a temporary inode, then atomically exchanging directory data fork contents back into the target.

## Key Functions

- `xrep_setup_directory()` enables directory hooks, creates orphanage/tempdir resources, and allocates repair state.
- `xrep_directory()` is the top-level repair entry point.
- `xrep_dir_find_parent()` finds the target directory parent from self-reference, dcache, dotdot lookup, or filesystem scan.
- `xrep_dir_find_entries()` salvages shortform or block/data-format dirents when parent pointers are unavailable.
- `xrep_dir_scan_dirtree()` rebuilds from parent pointers and child directory scans when parent pointers are enabled.
- `xrep_dir_live_update()` captures concurrent relevant directory updates into the tempdir replay queue.
- `xrep_dir_stash_createname()` and `xrep_dir_stash_removename()` record batched tempdir updates in `xfarray`/`xfblob`.
- `xrep_dir_replay_updates()` flushes stashed updates to the temporary directory.
- `xrep_dir_rebuild_tree()` finalizes tempdir updates, swaps directory data fork contents, resets the old tempdir fork, and releases tempdir locks.
- `xrep_dir_swap()` handles dotdot reset, shortform copyout, mapping exchange preparation, link count reset, and atomic content exchange.
- `xrep_dir_set_nlink()` recalculates directory link count and removes revived directories from the unlinked list when needed.
- `xrep_dir_move_to_orphanage()` attaches a rebuilt parentless directory to lost+found/orphanage.

## Repair Strategy

The file has two rebuild modes:

- Without parent pointers, salvage plausible old dirents from shortform or raw data blocks.
- With parent pointers, scan filesystem inodes for parent pointers and child dirents that reconstruct the directory.

Both modes batch updates to bound memory use, then commit through a temporary directory and atomic exchange-range support.

## Research Notes

Repair requires rmapbt for reaping old blocks and exchange-range support for atomic replacement. Directory hooks keep the rebuild synchronized with concurrent mutations while long scans temporarily drop locks.
