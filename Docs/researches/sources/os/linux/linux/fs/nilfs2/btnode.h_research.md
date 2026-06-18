# File Research: sources/os/linux/linux/fs/nilfs2/btnode.h

This header declares the B-tree node cache interface shared by NILFS2 bmap/B-tree, GC, metadata, and inode code.

Key contents:
- Defines `struct nilfs_btnode_chkey_ctxt`, the state carrier for changing a cached node’s key:
  - `oldkey`, `newkey`
  - current `bh`
  - optional replacement `newbh`
- Declares cache lifecycle and buffer APIs:
  - cache inode init and cache clear
  - node block create/read-submit/delete
  - prepare/commit/abort key change

Important role:
- This is the boundary between generic B-tree logic and the special associated-inode cache used to store non-leaf B-tree nodes separately from file data pages.
- The change-key context is central to copy-on-write pointer updates where B-tree node blocks receive new virtual or physical addresses.
