# File Research: sources/os/linux/linux-stable/fs/hpfs/anode.c

## Purpose

Manages HPFS allocation B+ trees in fnodes and anodes, including lookup, append, truncation, EA data access, and recursive-free logic.

## Main Entry Points

- `hpfs_bplus_lookup()`: maps file sector numbers to disk sectors.
- `hpfs_add_sector_to_btree()`: appends a sector, splitting B+ tree nodes as needed.
- `hpfs_remove_btree()` and `hpfs_truncate_btree()`: free or shrink allocation trees.
- `hpfs_ea_read()`, `hpfs_ea_write()`, `hpfs_ea_remove()`: access EA storage through direct extents or anodes.
- `hpfs_remove_fnode()`: frees a file or directory fnode, allocation tree/dtree, and EAs.

## Control Flow And State

B+ trees are either leaf extent arrays or internal anode-pointer arrays. Lookup descends internal nodes until a leaf contains the requested file sector, updating the inode’s allocation cache. Appending first attempts to extend the final extent contiguously; otherwise it allocates a new sector and inserts a leaf node, splitting anodes upward and possibly turning the fnode root into an internal node.

Removal avoids recursion to prevent stack overflow. Truncation walks down the subtree containing the truncation boundary, frees later subtrees or extents, and updates used/free node counts and first-free offsets.

## Dependencies

Depends on allocation helpers, fnode/anode mapping, cycle detection, sector validation, and B+ tree structure definitions from `hpfs.h`.

## Risks

This is a high-risk metadata mutation file. Split and root-promotion paths must keep `up` pointers, `BP_fnode_parent`, node counts, and `first_free` consistent. Some EA-anode creation paths are not implemented in `ea.c`, so EA users depend on fallback contiguous relocation.
