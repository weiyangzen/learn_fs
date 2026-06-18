# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass2.c

Purpose: implements fsck pass 2, iterating directory blocks discovered by pass 1, repairing directory entry structure/content, counting directory-entry references, and building parent linkage for pass 3.

Read coverage: complete file read, 1,049 lines.

Key responsibilities:
- Tests directory entry inode targets for allocation and range validity.
- Validates and repairs `.` and `..` entries, including inline-directory offsets and parent tracking.
- Repairs directory block trailer compatibility fields, block number, and parent inode fields.
- Detects and repairs corrupt `rec_len` / `name_len` combinations enough to continue scanning, or wipes the rest of an unsafe block into a deleted entry.
- Clears zero-length names, invalid inode references, and duplicate parent claims for subdirectories.
- Replaces invalid slash/NUL name characters with dots.
- Synchronizes dirent `file_type` with the referenced inode type.
- Detects duplicate names within bounded in-memory windows and renames duplicates by adding/replacing underscores.
- Checks indexed directory lookup consistency, schedules index rebuilds, and truncates invalid index trees on filesystems without indexed-dir support.
- Optionally compresses directory entries by moving live entries forward.

Important entry points:
- `o2fsck_pass2()` allocates buffers, initializes duplicate-name tracking, seeds root/system parent records, iterates directory blocks, and rebuilds marked indexed dirs.
- `pass2_dir_block_iterate()` is the main per-directory-block callback.
- `fix_dirent_dots()`, `fix_dirent_lengths()`, `fix_dirent_name()`, `fix_dirent_inode()`, `fix_dirent_filetype()`, `fix_dirent_linkage()`, `fix_dirent_dups()`, and `fix_dirent_index()` perform individual repair classes.
- `release_re_idx_dirs_rbtree()` frees rebuild-tracking entries.
- `o2fsck_test_inode_allocated()` wraps allocation tests with conservative fallback.

Dependencies:
- Uses directory block tracking from pass 1, dir-parent rbtrees, icount maps, the string rbtree helper from `strings.c`, libocfs2 directory read/write/lookup/index APIs, and prompt problem codes.

Risk and edge cases:
- Duplicate-name detection is intentionally bounded; when the string rbtree exceeds 4 MiB it is reset, so it does not guarantee whole-directory duplicate detection.
- If a dirent’s length fields are too corrupt to trust, the code wipes the remaining block area rather than risk parsing filename bytes as entries.
- Inline directory blocks are repaired by copying the whole inode block image and writing the inode.
- Indexed directory repair is deferred by recording directories for rebuild after block iteration.
- `o2fsck_test_inode_allocated()` treats allocation-test errors as allocated to avoid cascading destructive repairs from uncertain state.
