# File Research: sources/local-fs/e2fsprogs/e2fsck/dirinfo.c

## Purpose
Maintains e2fsck’s directory information database: inode number, `..` parent, and tree-walk parent. This avoids repeated directory I/O across passes.

## Data Model
- `struct dir_info_db` stores count/size, in-memory sorted array, last lookup cache, and optional TDB scratch-file state.
- `struct dir_info` entries are sorted by inode number.
- `struct dir_info_iter` abstracts array and TDB iteration.

## Main Behavior
- `setup_db()` initializes the database, using `ext2fs_get_num_dirs()` to size the array.
- With `CONFIG_TDB`, `setup_tdb()` can switch directory info storage to a temporary TDB file based on profile settings under `scratch_files`.
- `e2fsck_add_dir_info()` inserts entries in inode order, handling rare out-of-order inserts by shifting entries.
- `e2fsck_get_dir_info()` does cached lookup, TDB lookup, or binary search.
- Setter/getter functions update or read `parent` and `dotdot`.
- Iteration supports both array traversal and TDB key traversal.
- `e2fsck_free_dir_info()` closes/deletes TDB scratch files and releases arrays.

## Integration
Created during pass 1 and filled/used by later directory passes for connectivity, `..` validation, and parent lookups. Its public API is declared in `e2fsck.h`.

## Risks / Notes
- TDB mode uses a temporary file derived from filesystem UUID and configured scratch directory.
- Array mode depends on sorted insertion for binary search correctness.
