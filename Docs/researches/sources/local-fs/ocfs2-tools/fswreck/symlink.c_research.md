# File Research: sources/local-fs/ocfs2-tools/fswreck/symlink.c

This file creates and corrupts symbolic links.

Key behavior:
- Uses fixed target text `"/dummy00/dummy00"`.
- `fillup_block()` fills a block with repeated dummy text and is used as a block-iterator callback.
- `add_symlink()` maps the first allocated block of a symlink inode, writes the dummy target, and sets inode size.
- `create_symlink()` creates a symlink inode, links it into a directory, allocates one cluster, and initializes its target data.
- `corrupt_symlink_file()` validates the inode is a symlink, then applies:
  - `LINK_FAST_DATA`: set `i_clusters` to zero
  - `LINK_NULLTERM`: fill all blocks with dummy text and set size to a full cluster
  - `LINK_SIZE`: inflate `i_size`
  - `LINK_BLOCKS`: inflate first extent record’s `e_leaf_clusters`
- `mess_up_symlink()` creates a symlink and corrupts it.

Integration notes:
- Uses block iteration and cached inode helpers from libocfs2.
- Creates non-fast symlinks by allocating a cluster before corruption.
