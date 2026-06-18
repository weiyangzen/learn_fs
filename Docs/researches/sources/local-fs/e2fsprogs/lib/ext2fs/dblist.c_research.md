# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/dblist.c

Implements directory block list management. A dblist is a growable array of `struct ext2_db_entry2` records sorted by block, inode, and logical block count.

Core APIs:
- `ext2fs_init_dblist`
- `ext2fs_copy_dblist`
- `ext2fs_add_dir_block2`
- `ext2fs_set_dir_block2`
- `ext2fs_dblist_sort2`
- `ext2fs_dblist_iterate3`
- `ext2fs_dblist_iterate2`
- `ext2fs_dblist_count2`
- `ext2fs_dblist_get_last2`
- `ext2fs_dblist_drop_last`

Legacy 32-bit APIs wrap the 64-bit versions: `ext2fs_add_dir_block`, `ext2fs_set_dir_block`, `ext2fs_dblist_sort`, `ext2fs_dblist_iterate`, `ext2fs_dblist_count`, and `ext2fs_dblist_get_last`.

Behavior:
- Initial capacity is either caller-provided or roughly twice the directory count plus 12.
- Appending grows capacity by 100 entries for small lists or 50% for larger lists.
- Iteration sorts lazily if the list is dirty.
- `DBLIST_ABORT` from callbacks stops iteration without returning an error.

Implementation notes:
- Legacy `ext2fs_dblist_get_last` returns a pointer to a static converted 32-bit entry, so it is not reentrant.
- Sorting can use either the native 64-bit comparator or a caller-provided legacy comparator via a global `sortfunc32`.
