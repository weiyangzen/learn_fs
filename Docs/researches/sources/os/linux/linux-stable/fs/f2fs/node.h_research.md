# File Research: sources/os/linux/linux-stable/fs/f2fs/node.h

## Purpose

`node.h` defines F2FS node-manager constants, NAT/free-nid data structures, node footer helpers, NAT address helpers, node-tree offset rules, and inline utilities for manipulating node ids and node flags.

## NAT and Free Nid Constants

- `START_NID(nid)`
  - Aligns a nid to the first nid in its NAT block.

- `NAT_BLOCK_OFFSET(start_nid)`
  - Converts a start nid to NAT block offset.

- `FREE_NID_PAGES`
  - Number of NAT pages to scan synchronously when building free nids.

- `MAX_FREE_NIDS`
  - Maximum normal free nid cache target derived from NAT entries per block and scanned pages.

- `SHRINK_NID_BATCH_SIZE`
  - Batch size when shrinking free nid cache.

- `DEF_RA_NID_PAGES`
  - Default NAT readahead pages for nid scanning.

- `MAX_RA_NODE`
  - Maximum node readahead size during data block lookup.

- `DEF_RAM_THRESHOLD`
  - Default memory threshold factor.

- `DEF_DIRTY_NAT_RATIO_THRESHOLD`
  - Dirty NAT ratio threshold.

- `DEF_NAT_CACHE_THRESHOLD`
  - Hard threshold for total cached NAT entries.

- `DEF_RF_NODE_BLOCKS`
  - Default roll-forward node block limit.

- `NAT_VEC_SIZE`
  - Gang lookup vector size for NAT cache/set scans.

- `LOCKED_PAGE`
  - Special return value from node read path.

- `FILE_NOT_ALIGNED`
  - Pinned-file alignment status constant.

## NAT Entry State

- Node info flags:
  - `IS_CHECKPOINTED`
  - `HAS_FSYNCED_INODE`
  - `HAS_LAST_FSYNC`
  - `IS_DIRTY`
  - `IS_PREALLOC`

- `struct node_info`
  - `nid`: node id.
  - `ino`: owning inode number.
  - `blk_addr`: physical node block address.
  - `version`: NAT version.
  - `flag`: in-memory state bits.

- `struct nat_entry`
  - List linkage plus cached `node_info`.

- NAT accessor macros
  - Get/set nid, block address, inode number, and version.

- `copy_node_info()`
  - Copies persistent node info fields but intentionally does not copy flags.

- `set_nat_flag()`, `get_nat_flag()`, `nat_reset_flag()`
  - Manage NAT state bits.
  - Reset makes an entry checkpointed, clears fsynced-inode marker, and marks last-fsync true.

- `node_info_from_raw_nat()` / `raw_nat_from_node_info()`
  - Convert between on-disk little-endian NAT entries and in-memory `node_info`.

- `excess_dirty_nats()` / `excess_cached_nats()`
  - Test dirty NAT ratio and total NAT cache pressure.

## Memory Type Enum

`enum mem_type` defines memory accounting categories used by node and cache pressure logic:

- `FREE_NIDS`
- `NAT_ENTRIES`
- `DIRTY_DENTS`
- `INO_ENTRIES`
- `READ_EXTENT_CACHE`
- `AGE_EXTENT_CACHE`
- `DISCARD_CACHE`
- `COMPRESS_PAGE`
- `BASE_CHECK`

## NAT Set and Free Nid Structures

- `struct nat_entry_set`
  - Groups dirty NAT entries by NAT block.
  - Contains set list, entry list, set number, and entry count.

- `struct free_nid`
  - Tracks a free or preallocated nid.
  - Contains list linkage, nid, and state.

- `next_free_nid()`
  - Peeks at first free nid under `nid_list_lock`.

## NAT Bitmap and Address Helpers

- `get_nat_bitmap()`
  - Copies current NAT bitmap, with optional mirror check under `CONFIG_F2FS_CHECK_FS`.

- `current_nat_addr()`
  - Computes physical NAT block address for a start nid using NAT bitmap to select old/new NAT copy.

- `next_nat_addr()`
  - Computes alternate NAT block address by flipping segment-copy bit.

- `set_to_next_nat()`
  - Toggles NAT bitmap for a NAT block, and mirror bitmap under checkfs.

## Node Footer Helpers

- `ino_of_node()`
  - Reads footer owner inode number.

- `nid_of_node()`
  - Reads footer nid.

- `ofs_of_node()`
  - Extracts logical node offset from footer flag bits.

- `cpver_of_node()`
  - Reads checkpoint version stored in footer.

- `next_blkaddr_of_node()`
  - Reads footer next-block pointer used by roll-forward recovery chain.

- `fill_node_footer()`
  - Initializes nid, ino, and offset in a node footer.
  - Optionally clears the node body.
  - Preserves non-offset flag bits when not resetting.

- `copy_node_footer()`
  - Copies only node footer between folios.

- `fill_node_footer_blkaddr()`
  - Stores checkpoint version/CRC and next block address for recovery.

- `is_recoverable_dnode()`
  - Checks whether a node footer checkpoint version matches current checkpoint recovery expectations.
  - Handles no-CRC and CRC recovery modes.

## Node Offset Topology

The comment documents F2FS node offset layout:

- Inode block is offset `0`.
- Direct nodes occupy offsets `1` and `2`.
- First indirect node is offset `3`; its direct children begin at `4`.
- Second indirect node starts at `4 + NIDS_PER_BLOCK`.
- Double-indirect node starts at `5 + 2 * NIDS_PER_BLOCK`.
- Double-indirect children use a repeated indirect/direct-node offset pattern.

## Node Type and Nid Access

- `IS_DNODE()`
  - Determines whether a node folio is a direct node carrying data addresses.
  - Treats xattr blocks as dnodes.
  - Excludes known indirect and double-indirect node offsets.

- `set_nid()`
  - Writes a child nid into inode or indirect node nid array.
  - Waits for node folio writeback and marks folio dirty.

- `get_nid()`
  - Reads child nid from inode or indirect node nid array.

## Cold/Fsync/Dentry Marks

- `is_node()`
  - Tests a footer flag bit.

- Macros:
  - `is_cold_node()`
  - `is_fsync_dnode()`
  - `is_dent_dnode()`

- `__set_mark()`
  - Sets or clears a footer flag bit.

- `set_cold_node()`
  - Marks non-directory node blocks cold.

- `set_mark()`
  - Sets a footer mark and updates inode checksum under checkfs.

- Macros:
  - `set_dentry_mark()`
  - `set_fsync_mark()`

## Interactions

- Used heavily by `node.c` for NAT, node footer, dnode classification, and writeback/recovery state.
- Used by `recovery.c` to validate roll-forward node chains and interpret fsync/dentry marks.
- Used by namespace and data paths through exported node helpers in `f2fs.h`.
