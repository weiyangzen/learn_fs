# File Research: sources/os/linux/linux/fs/f2fs/node.h

Header for F2FS node manager structures, constants, NAT address helpers, node footer helpers, node tree offset logic, and node mark helpers.

Key constants:
- NAT addressing: `START_NID()`, `NAT_BLOCK_OFFSET()`.
- Free-NID scan/cache limits: `FREE_NID_PAGES`, `MAX_FREE_NIDS`, `SHRINK_NID_BATCH_SIZE`, `DEF_RA_NID_PAGES`.
- Node readahead: `MAX_RA_NODE`.
- Memory/cache thresholds: `DEF_RAM_THRESHOLD`, `DEF_DIRTY_NAT_RATIO_THRESHOLD`, `DEF_NAT_CACHE_THRESHOLD`.
- Roll-forward control: `DEF_RF_NODE_BLOCKS`.
- Lookup vector size: `NAT_VEC_SIZE`.
- `LOCKED_PAGE` read-node sentinel and `FILE_NOT_ALIGNED`.

Core structures:
- `struct node_info`: in-memory NAT information for one NID: nid, owner ino, block address, version, and flags.
- `struct nat_entry`: cached NAT entry with list linkage.
- `struct nat_entry_set`: group of dirty NAT entries belonging to one NAT block.
- `struct free_nid`: cached free or preallocated NID entry.

NAT helpers:
- Accessors for nid, block address, owner ino, and version.
- `nat_reset_flag()` resets checkpoint/fsync-related NAT flags after persistence.
- `node_info_from_raw_nat()` and `raw_nat_from_node_info()` convert between on-disk NAT entries and in-memory `node_info`.
- `excess_dirty_nats()` and `excess_cached_nats()` implement threshold checks.

NAT block addressing:
- `get_nat_bitmap()` copies the current NAT version bitmap and optionally verifies its mirror.
- `current_nat_addr()` maps a start NID to the active NAT block copy.
- `next_nat_addr()` returns the alternate NAT block copy.
- `set_to_next_nat()` toggles the NAT version bitmap after NAT block copy-on-write.

Node footer helpers:
- `ino_of_node()`, `nid_of_node()`, `ofs_of_node()`, `cpver_of_node()`, `next_blkaddr_of_node()`.
- `fill_node_footer()` initializes or updates node footer nid/ino/offset while preserving mark bits when requested.
- `copy_node_footer()` copies footer state between node pages.
- `fill_node_footer_blkaddr()` records checkpoint version/CRC and next block address for roll-forward chaining.
- `is_recoverable_dnode()` checks whether a node page belongs to the current recoverable checkpoint version.

Node tree helpers:
- `IS_DNODE()` classifies data nodes versus indirect nodes using F2FS node offset layout.
- `set_nid()` and `get_nid()` read/write child NIDs in inode or indirect node blocks.

Cold/fsync/dentry marks:
- `is_cold_node()`, `is_fsync_dnode()`, `is_dent_dnode()` inspect footer mark bits.
- `set_cold_node()`, `set_dentry_mark()`, `set_fsync_mark()` update footer marks and refresh inode checksum under check-FS builds.

Memory type enum:
- `enum mem_type` names memory-pressure accounting categories shared with `node.c`, including free NIDs, NAT entries, dirty dentries, inode entries, extent caches, discard cache, compressed pages, and base checks.
