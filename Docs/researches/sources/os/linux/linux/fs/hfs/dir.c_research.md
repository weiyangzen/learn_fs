# File Research: sources/os/linux/linux/fs/hfs/dir.c

Purpose: Provides classic HFS directory VFS operations: lookup, readdir, create, mkdir, unlink/rmdir, rename, and operation tables.

Key functions:
- `hfs_lookup()` builds a catalog key from parent inode and dentry name, reads the catalog record, and returns `hfs_iget()` result via `d_splice_alias()`.
- `hfs_readdir()` emits synthetic `.` and `..`, then walks catalog records belonging to the directory using `hfs_brec_goto()`.
- `hfs_dir_release()` removes per-open readdir tracking from `open_dir_list`.
- `hfs_create()` and `hfs_mkdir()` allocate a new inode and add catalog entries.
- `hfs_remove()` checks directory emptiness, validates CNID counters, removes catalog entries, and clears the inode link.
- `hfs_rename()` supports only `RENAME_NOREPLACE`, removes existing destination, and updates the moved inode's cached catalog key.

Dependencies and integration:
- Uses catalog operations from `catalog.c`, inode constructors/deletion from `inode.c`, and B-tree search helpers.
- Maintains `hfs_readdir_data` so catalog deletion can adjust active directory file positions.

Risk notes:
- Directory `i_size` is treated as catalog valence plus two synthetic entries; bad catalog valence can affect iteration limits.
- `hfs_remove()` blocks mutation if CNID/file/folder counters exceed 32-bit limits.
