# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/initialize.c

## Purpose
Bootstraps `fsck.gfs2` against a target device. It opens the device safely, reads or repairs the superblock, blocks concurrent mounters when safe, initializes resource groups and system inodes, replays journals, checks resource group integrity, and tears down global fsck state.

## Main Elements
- `block_mounters()`: rewrites the superblock lock protocol prefix between `lock_` and `fsck_` to discourage mounting while fsck runs.
- Tree cleanup helpers: `dup_free()`, `dirtree_free()`, `inodetree_free()`, and `empty_super_block()`.
- `set_block_ranges()`: derives `first_data_block`, `last_data_block`, `last_fs_block`, and verifies the highest block can be read.
- `check_rgrp_integrity()` / `check_rgrps_integrity()`: recompute resource-group bitmap counts, optionally reclaim unlinked dinodes, and repair `rt_free`.
- `rebuild_sysdir()`: rebuilds the master system directory and reconnects or recreates `jindex`, `per_node`, `inum`, `statfs`, `rindex`, and `quota`.
- `lookup_per_node()`: finds or later rebuilds the `per_node` directory.
- `read_rgrps()`, `fetch_rgrps_level()`, `fetch_rgrps()`: read and validate the rindex/resource group set across escalating trust/rebuild levels.
- `init_system_inodes()`: loads root, inum, statfs, quota, per_node, and computes filesystem boundaries.
- Superblock repair path: `find_rgs_for_bsize()`, `peruse_metadata()`, `peruse_system_dinode()`, `peruse_user_dinode()`, and `sb_repair()`.
- `initialize()`: top-level setup called by `main.c`.
- `destroy()`: unblocks mounters, fsyncs, frees trees/resource groups, closes the device, and drops caches after mounted-read-only repairs when possible.

## Control Flow
`initialize()` opens the device read-only for `-n` or read-write exclusive otherwise. If exclusive open fails because the device is mounted read-only, it allows a limited root-filesystem style check. It then reads the device info, reads or repairs the superblock, blocks mounters if preen policy permits, reads or rebuilds the master directory, locates `per_node`, initializes `rindex`, fetches resource groups, reads and replays journals, marks the filesystem clean for preen if all journals were clean, then initializes the remaining system inodes.

## Dependencies And Integration
Uses libgfs2 superblock, inode, rindex, rgrp, bitmap, and builder APIs; journal recovery from `fs_recovery.h`; metadata helpers from `metawalk.h`; inode tree deletion from `inode_hash.h`; and query/logging utilities from `util.h`. Globals initialized here are consumed by later passes, especially `last_fs_block`, `first_data_block`, and `last_data_block`.

## Risk Notes
This file contains high-impact recovery logic: superblock reconstruction, root/master guessing, system inode rebuilding, rgrp count correction, and lock protocol rewriting. Most destructive paths are query-gated, but correctness depends on recovered metadata heuristics and on restoring the lock protocol in `destroy()`.
