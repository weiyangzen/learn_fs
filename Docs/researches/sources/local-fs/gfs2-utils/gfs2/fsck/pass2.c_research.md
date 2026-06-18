# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/pass2.c

This file implements `fsck.gfs2` pass 2, the pathname and directory-content validation pass. It walks system directories and all discovered directory inodes, validates directory entries, repairs malformed entries when permitted, builds parent/dotdot relationship state, and increments the in-memory link-count accounting consumed by later passes.

Key control flow centers on `pass2()`, which checks `jindex`, `per_node`, `master`, and `root` via `check_system_dir()`, then iterates `cx->dirtree` and calls `pass2_check_dir()` for non-system directories. Directory walking is delegated through `struct metawalk_fxns pass2_fxns`, especially `check_dentry()` and `check_hash_tbl()`.

Important behaviors:
- Validates dentry target block range, record/name length, hash value, bitmap type, file type, and formal inode number.
- Handles `.` and `..` specially, recording `dotdot_parent` and `treewalk_parent` in `struct dir_info`.
- Detects and optionally clears duplicate `.`/`..`, stale file-type entries, hard links to directories, entries pointing to invalid/non-inode blocks, and bad formal inode references.
- Repairs exhash directory hash table/leaf corruption using `check_hash_tbl()`, `fix_hashtable()`, `wrong_leaf()`, `lost_leaf()`, `pad_with_leafblks()`, and `write_new_leaf()`.
- Validates per-node system files `inum_rangeN`, `statfs_changeN`, and `quota_changeN`, rebuilding missing or malformed files through libgfs2 builders.
- Relocates entries from misplaced leaves into `lost+found` when recovery cannot safely preserve their original leaf placement.

Dependencies include `libgfs2`, `metawalk`, `link`, `lost_n_found`, inode/directory trees, fsck bitmap helpers, and recovery/build functions. The file is mutation-heavy: repairs mark buffers modified, update bitmaps, allocate leaves, delete dentries, and adjust link counts.

Risks and notes:
- Recovery paths rely on interactive `query()` decisions, so behavior differs under yes/no modes.
- Hash-table repair is complex and can reprocess indices after mutations; incorrect leaf-depth or pointer-count assumptions would affect directory lookup semantics.
- `lost_leaf()` uses fixed buffers and has a suspicious filename-length check against `sizeof(filename)` where `filename` is a pointer, which could prematurely stop processing long names.
- This pass establishes state needed by pass3/pass4, so missed link increments or parent recording errors cascade into connectivity and nlink repair.
