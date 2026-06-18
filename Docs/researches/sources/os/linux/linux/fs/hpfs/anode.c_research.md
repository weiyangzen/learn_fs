# File Research: sources/os/linux/linux/fs/hpfs/anode.c

Purpose: Manages HPFS allocation B+ trees stored in fnodes and anodes, including lookup, growth, removal, EA data I/O, and truncation.

Key functions:
- `hpfs_bplus_lookup()` descends internal anodes and finds the disk sector for a file sector, updating the inode’s small extent cache.
- `hpfs_add_sector_to_btree()` appends a sector to an allocation tree, extends the last extent when possible, allocates sectors otherwise, and creates/splits anodes as needed.
- `hpfs_remove_btree()` iteratively frees all extents and anodes without recursion.
- `hpfs_ea_read()` and `hpfs_ea_write()` read/write EA byte ranges through direct sectors or anode-backed allocation trees.
- `hpfs_ea_remove()` frees direct or anode-backed EA storage.
- `hpfs_truncate_btree()` frees sectors beyond a target file-sector count and trims tree metadata.
- `hpfs_remove_fnode()` removes file/directory data trees, indirect EAs, external EA lists, and finally the fnode sector.

Dependencies and integration:
- Uses `hpfs_map_fnode()`, `hpfs_map_anode()`, sector allocation/freeing, and dnode tree removal.
- Core to file writes/truncates, EA storage, and inode eviction.

Risk notes:
- Tree manipulation is complex and assumes append-style growth for files.
- Cycle detection is conditional on check mode.
- Truncation intentionally does not rebalance/join anodes.
