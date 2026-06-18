# File Research: sources/os/linux/linux/fs/squashfs/namei.c

Implements directory name lookup.

SquashFS directories are sorted and grouped by directory headers sharing inode start blocks. Long directories may include an index mapping names to metadata blocks; `get_dir_index_using_name()` linearly scans this index to jump near the target.

`squashfs_lookup()` validates name length, reads directory headers and entries, stops early when sorted ordering proves absence, and instantiates matching inodes with `squashfs_iget()`.

Exports `squashfs_dir_inode_ops` with lookup and xattr listing.
