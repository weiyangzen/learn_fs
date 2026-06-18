# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_readinode.c

Purpose: Reconstructs in-memory inode state from append-log data nodes. It validates data nodes, resolves overlapping versions, builds the file fragment tree, truncates to vnode size, and services data reads.

Key areas:
- Red-black tree comparators for temporary data nodes and live fragments.
- Temporary data-node validation and overlap resolution.
- Fragment insertion, truncation, and obsolete handling.
- Inode read/replay and file data read.

Main entry points:
- `chfs_read_inode`: state-gated public inode read.
- `chfs_read_inode_internal`: builds temporary node tree, builds final fragment tree, applies vnode metadata size.
- `chfs_get_data_nodes`: reads data-node headers from vnode-cache data-node refs.
- `chfs_build_fragtree`: selects valid latest data nodes and populates `ip->fragtree`.
- `chfs_add_full_dnode_to_inode`: turns a full dnode into one or more fragments.
- `chfs_truncate_fragtree`, `chfs_kill_fragtree`, `chfs_remove_frags_of_node`.
- `chfs_read_data`: reads a page/block through the fragment tree and verifies header/node/data CRCs.

Important behavior:
- Initial scan marks data nodes unchecked; this file validates only surviving relevant data nodes during inode replay.
- Overlapping data nodes are resolved using version ordering and offset ranges.
- Hole fragments are represented with `node == NULL`.
- Superseded nodes are obsoleted through `chfs_remove_and_obsolete`.
- Partial-page boundary cases mark adjacent node refs normal rather than pristine.
- `chfs_read_data` zero-fills the buffer first, then overlays node data if a fragment covers the requested offset.

Dependencies:
- Uses node-ref and obsolete helpers from `chfs_nodeops.c`.
- Uses allocation helpers from `chfs_malloc.c`.
- Uses `chfs_read_leb` for flash reads and CRC helpers from CHFS headers.

Research notes:
- There are memory-management quirks: `chfs_get_data_nodes` allocates both `buf` and `dnode`, then reassigns `dnode` to `buf`.
- Some error paths are marked FIXME and may leave partially built fragment state.
- `chfs_remove_frags_of_node` assumes fragments with matching nref have non-null `node`.
