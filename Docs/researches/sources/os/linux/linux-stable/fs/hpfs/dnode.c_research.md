# File Research: sources/os/linux/linux-stable/fs/hpfs/dnode.c

## Purpose

Implements HPFS directory dnode tree operations: dirent insertion, deletion, lookup, traversal, position repair, dnode splitting/merging, and empty-directory cleanup.

## Main Entry Points

- `hpfs_add_pos()` / `hpfs_del_pos()`: track live readdir positions.
- `hpfs_add_de()` and `hpfs_add_dirent()`: insert directory entries.
- `hpfs_remove_dirent()`: delete directory entries and rebalance.
- `hpfs_count_dnodes()`: count directory blocks, subdirectories, and items.
- `map_pos_dirent()`, `map_dirent()`, `map_fnode_dirent()`: traversal/search helpers.
- `hpfs_remove_dtree()`: frees an empty directory tree.
- `hpfs_de_as_down_as_possible()`: finds the leftmost reachable dnode for iteration.

## Control Flow And State

Dnodes form a B-tree-like sorted directory tree. Insertions descend by HPFS name comparison, then either fit a new dirent into the current dnode or split the dnode, allocating sibling/root dnodes and promoting a separator dirent upward. Deletions remove a dirent, optionally move the predecessor/successor from a child subtree to the top, and delete empty dnodes while repairing parent down pointers and root dnode ownership.

The file maintains active `loff_t *` directory positions for open readdir streams. Mutation helpers substitute, insert, or delete encoded positions so concurrent directory iteration remains coherent.

## Dependencies

Depends on allocation/free dnode helpers, four-sector dnode mapping, fnode mapping, name comparison, cycle detection, and HPFS inode directory state.

## Risks

This is the most complex HPFS mutation code. ENOSPC during split/delete can corrupt the directory tree, so callers preflight free dnode availability. Position-repair logic is fragile and encodes sentinel values such as `4`, `5`, and `12`. Corrupt up/down pointers are detected in strict check modes but often only log errors before returning.
