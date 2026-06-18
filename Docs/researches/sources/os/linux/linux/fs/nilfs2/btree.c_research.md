# File Research: sources/os/linux/linux/fs/nilfs2/btree.c

This file implements NILFS2’s B-tree-backed block mapping operations. It provides lookup, contiguous lookup, insertion, deletion, key seeking, conversion from direct maps, dirty propagation, block assignment during segment construction, GC variants, and corruption checks for B-tree nodes.

Core structure:
- Operations work over arrays of `struct nilfs_btree_path`, one per tree level.
- The root node is stored inline in the `nilfs_bmap`; non-root nodes live in the associated B-tree node cache.
- Nodes contain sorted disk keys and pointers. Root and non-root layouts differ by an extra padding area in non-root nodes.
- Node capacity is derived from block size and macros in `btree.h`.

Lookup path:
- `nilfs_btree_do_lookup()` descends from root to the requested minimum level using binary search inside each node.
- `__nilfs_btree_get_block()` reads non-root node blocks through `btnode.c`, performs optional sibling readahead near leaves, waits for I/O, validates node blocks, and converts invalid virtual translations into metadata-corruption style errors.
- `nilfs_btree_lookup_contig()` walks adjacent leaf entries and right siblings to return runs of physically contiguous blocks, translating virtual block numbers through DAT when needed.

Mutation path:
- Insert preparation allocates a data pointer and, when needed, node pointers through `nilfs_bmap_prepare_alloc_ptr()`.
- Insert commit uses one of several operations:
  - direct insert into a node/root
  - carry entries left or right into a sibling
  - split a full node
  - grow the tree by moving the old root contents into a child node
- Delete preparation ends old pointers and chooses:
  - direct delete
  - borrow from left/right sibling
  - concatenate with sibling
  - shrink the tree if the root can collapse
- Commit/abort sequencing is explicit so pointer allocation/free state stays consistent with bmap modifications.

Conversion:
- `nilfs_btree_convert_and_insert()` converts gathered direct-map entries plus a new entry into a B-tree.
- If all entries fit in the inline root, only the root is created.
- If they exceed root capacity but fit in one node block, a level-1 child node plus level-2 root are created.

Dirty propagation and segment construction:
- `nilfs_btree_propagate()` finds the B-tree path for a dirty data or node buffer.
- Physical-pointer mode only dirties ancestor node buffers.
- Virtual-pointer mode may allocate a new DAT entry and relocate cached node buffers with `nilfs_btnode_prepare_change_key()`/commit/abort.
- Assignment operations fill `union nilfs_binfo` for log writing:
  - physical mode updates parent pointers to physical block numbers
  - virtual mode starts DAT entries with assigned physical block numbers
  - GC assignment uses `nilfs_dat_move()`

Dirty-buffer ordering:
- `nilfs_btree_lookup_dirty_buffers()` scans dirty folios in the node cache and orders buffers by B-tree level and first key. This gives segment construction a deterministic view of dirty metadata nodes.

Corruption handling:
- `nilfs_btree_node_broken()` validates non-root nodes: level range, root flag absence, positive child count, and max child count.
- `nilfs_btree_root_broken()` validates root level and child count.
- `nilfs_btree_bad_node()` detects level mismatch during descent.
- I/O errors and bad metadata are reported through NILFS logging and typically surfaced as `-EIO` or `-EINVAL`.

Exported operations:
- `nilfs_btree_init()` installs normal bmap operations and attaches the B-tree node cache after root validation.
- `nilfs_btree_init_gc()` installs restricted GC operations for propagation and assignment only.
- `nilfs_btree_broken_node_block()` is shared by GC/node-read paths to validate cached node buffers.

Important invariants:
- Non-root node buffers must have valid level metadata matching the traversal level.
- Pointer lifecycle is two-phase: prepare alloc/end first, then commit with tree mutation; abort paths unwind prepared resources.
- Virtual block mode depends on DAT locks and DAT lifetime updates to avoid exposing uncommitted physical placements.
