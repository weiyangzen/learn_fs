# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/metawalk.c

## Purpose
Provides the callback-driven metadata traversal and repair engine used by GFS2 fsck passes. It walks inode metadata trees, directory hash/leaf structures, directory entries, data pointers, and extended attributes while delegating pass-specific decisions to `struct metawalk_fxns`.

## Main Elements
- Bitmap synchronization:
  - `check_n_fix_bitmap()` compares discovered block state to rgrp bitmap state, query-repairs mismatches, and updates rgrp free/dinode counts.
  - `_fsck_bitmap_set()` wraps bitmap repair with debug tracing.
- Inode helpers:
  - `dupfind()` searches duplicate-block tree.
  - `fsck_system_inode()`, `fsck_load_inode()`, `fsck_inode_get()`, `fsck_inode_put()` special-case system inodes and `lost+found`.
- Directory entry/leaf checking:
  - `dirent_repair()` and `dirblk_truncate()` repair corrupt directory entry lengths or truncate a block.
  - `check_entries()` walks linear or leaf directory entries and calls pass-specific `check_dentry`.
  - `check_leaf()` validates one exhash leaf, repairs bad leaf pointers, checks entries, and fixes leaf entry counts.
  - `check_leaf_blks()` reads the directory hash table, readaheads leaves, validates chained leaves, and adapts to directory depth/height changes.
  - `check_linear_dir()` and `check_dir()` expose directory checking for stuffed and exhash directories.
- Extended attributes:
  - `check_eattr_entries()` walks EA headers and extended data pointers.
  - `check_leaf_eattr()` validates one EA leaf.
  - `check_indirect_eattr()` walks indirect EA leaf pointer blocks and handles no-hole semantics.
  - `check_inode_eattr()` dispatches direct versus indirect EA validation.
- Metadata/data tree walking:
  - `build_and_check_metalist()` builds per-height metadata buffer lists and calls `check_metalist`.
  - `metawalk_check_data()` calls pass-specific `check_data` for data pointers.
  - `undo_check_data()` and metadata undo logic reverse pass work after unrecoverable errors.
  - `check_metatree()` is the main inode metadata walker and invalidates corrupt inodes when requested.

## Control Flow
Passes provide a `metawalk_fxns` table. `check_metatree()` builds metadata lists from the dinode outward, checks metadata blocks, branches to directory leaf checking for exhash directories, or checks regular data pointers for files. On fatal metadata/data errors, it can ask to remove the invalid inode, run pass-specific undo callbacks, delete duplicate references, and mark the dinode free.

## Dependencies And Integration
Used heavily by pass1, pass1b, lost+found repair, and later directory/link passes. Depends on libgfs2 buffer/inode/dir/EA APIs, duplicate tracking, link maps, directory/inode trees, and query/logging utilities.

## Risk Notes
This is a shared repair engine, so callback contracts are critical: callbacks must distinguish fatal errors, skip-one, skip-further, duplicate references, and valid blocks consistently. It intentionally performs query-gated destructive operations such as clearing bitmap states, truncating directory blocks, deleting EA chains, and invalidating inodes.
