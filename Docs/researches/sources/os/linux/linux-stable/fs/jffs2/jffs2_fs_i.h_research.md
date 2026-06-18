# File Research: sources/os/linux/linux-stable/fs/jffs2/jffs2_fs_i.h

## Role

Defines the JFFS2 private per-inode structure embedded in Linux `struct inode`.

## Main Structure

`struct jffs2_inode_info` contains:

- `sem`: JFFS2-specific inode mutex used instead of `i_rwsem` to avoid GC deadlocks.
- `highest_version`: highest raw dnode version for this inode.
- `fragtree`: red-black tree mapping logical file ranges to `jffs2_node_frag` records.
- `metadata`: metadata-only dnode not referenced by fragments, used for directories, symlinks, device nodes, and metadata updates.
- `dents`: linked list of directory entries for directory inodes.
- `target`: cached symlink target.
- `inocache`: always-resident inode cache entry.
- `flags`: inode flags.
- `usercompr`: user-selected compression byte.
- `vfs_inode`: embedded Linux inode.

## Research Notes

This structure is the in-core expanded form of a JFFS2 inode. The fragment tree is built only when the inode is instantiated, while the smaller inode cache remains available even when the VFS inode is absent.
