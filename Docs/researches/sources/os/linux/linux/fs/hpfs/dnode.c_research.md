# File Research: sources/os/linux/linux/fs/hpfs/dnode.c

Purpose: Implements HPFS directory dnode tree manipulation: lookup, insertion with splitting, deletion with balancing, position tracking, counting, and tree removal.

Key functions:
- `hpfs_add_pos()`, `hpfs_del_pos()`, and helper callbacks track active readdir offsets and update them during mutations.
- `hpfs_add_de()` inserts a dirent into a dnode in sorted order without splitting.
- `hpfs_add_to_dnode()` inserts into a dnode tree, splitting full dnodes, creating new root dnodes, and fixing child parent pointers.
- `hpfs_add_dirent()` descends the directory tree and inserts a new dirent, checking free dnode headroom first.
- `move_to_top()` and `delete_empty_dnode()` rebalance after deletion.
- `hpfs_remove_dirent()` removes a dirent and repairs/downshifts the dnode tree.
- `hpfs_count_dnodes()` counts dnodes, subdirectories, and items for inode metadata and emptiness checks.
- `hpfs_de_as_down_as_possible()` finds the leftmost reachable dnode for readdir start.
- `map_pos_dirent()` maps an encoded directory position to a dirent and advances to the next position.
- `map_dirent()` searches by name through the dnode tree.
- `hpfs_remove_dtree()` frees an empty directory tree.
- `map_fnode_dirent()` locates the directory entry for a given fnode, using the fnode’s truncated name as a search hint.

Dependencies and integration:
- Central to directory creation/removal/rename, readdir, lookup, inode writeback, and directory size/link counts.
- Uses allocation helpers, dnode mapping, name comparison, and global cycle checks.

Risk notes:
- This is the most structurally complex HPFS code; dnode splits/merges must preserve parent pointers, sentinel entries, sorted order, and active iterator positions.
- Several errors are reported as filesystem corruption because partial directory tree mutation can leave on-disk structures inconsistent.
