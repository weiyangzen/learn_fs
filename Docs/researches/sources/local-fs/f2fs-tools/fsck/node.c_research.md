# File Research: sources/local-fs/f2fs-tools/fsck/node.c

Purpose: provides F2FS node allocation, rebuilding, traversal, and update helpers used by fsck, sload, inject, and quota repair.

Key behavior:
- `f2fs_alloc_nid()` finds the first clear bit in `nm_i->nid_bitmap`, sets it, and returns the allocated NID.
- `f2fs_release_nid()` clears a previously allocated NID bit.
- `f2fs_rebuild_qf_inode()` creates a fresh quota inode node, initializes size/blocks/flags/footer version, reserves a hot node block, writes the inode, updates NAT, and adjusts fsck/NID bitmaps.
- `set_data_blkaddr()` updates the data address in inode or direct-node address arrays and marks inode/node dirty state in `dnode_of_data`.
- `new_node_block()` allocates a node page, fills footer fields, chooses hot/warm/cold node curseg based on dnode/directory/RO feature, reserves a block, updates NAT, and increments inode block count.
- `get_node_path()` maps a file page index into inode direct, direct node, indirect node, or double-indirect node path offsets and node offsets.
- `get_dnode_of_data()` walks or allocates node pages for a file offset, updating parent NIDs and writing parent nodes when allocating, then returns the target node, block address, and offset.
- `update_inode()` recomputes inode checksum when the feature is enabled, then delegates to `update_block()`.

Important dependencies:
- Uses node accessors from `node.h`, metadata updates from `mount.c`, and allocation helpers from segment code.
- `inject_dentry()` uses `get_dnode_of_data()` to find directory data blocks.

Risk notes:
- Allocation scans NIDs linearly from zero and asserts if none are free.
- `get_dnode_of_data()` reads a node even for zero NIDs in lookup modes; callers need valid file topology or sparse handling.
- New node allocation returns `0` on reserve failure, which callers convert to errors.
