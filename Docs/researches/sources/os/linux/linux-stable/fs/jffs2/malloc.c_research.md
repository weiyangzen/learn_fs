# File Research: sources/os/linux/linux-stable/fs/jffs2/malloc.c

## Role

Owns JFFS2 object allocation caches and typed allocation/free wrappers for core in-memory and raw-node helper structures.

## Slab Cache Lifecycle

- `jffs2_create_slab_caches()` creates caches for:
  - `jffs2_full_dnode`;
  - `jffs2_raw_dirent`;
  - `jffs2_raw_inode`;
  - `jffs2_tmp_dnode_info`;
  - raw node ref blocks;
  - `jffs2_node_frag`;
  - `jffs2_inode_cache`;
  - xattr datum/ref objects when configured.
- `jffs2_destroy_slab_caches()` destroys all created caches.

## Allocation Wrappers

Provides typed alloc/free functions for:

- full dirents, with variable name tail allocated by `kmalloc`;
- full dnodes;
- raw dirents;
- raw inodes;
- temporary dnode info;
- raw node ref blocks;
- node fragments;
- inode caches;
- xattr datum/ref structures when enabled.

## Raw Node Ref Blocks

- `jffs2_alloc_refblock()` allocates a block of raw node refs.
- Initializes usable slots as `REF_EMPTY_NODE`.
- Sets the final slot as `REF_LINK_NODE`, used to link to another ref block.
- `jffs2_prealloc_raw_node_refs()` walks or extends the refblock chain for an eraseblock and reserves a requested number of refs in `jeb->allocated_refs`.

## Research Notes

The file centralizes memory ownership for JFFS2’s small, high-churn metadata objects. Raw node refs are allocated in small linked blocks rather than one object at a time to reduce overhead while supporting per-eraseblock chains.
