# File Research: sources/os/linux/linux/fs/exfat/inode.c

## Purpose
Implements exFAT inode writeback, logical-to-physical block mapping, address-space operations, direct I/O integration, inode hash lookup, inode construction, and eviction.

## Main Interfaces
- `__exfat_write_inode`, `exfat_write_inode`, `exfat_sync_inode`
- `exfat_build_inode`, `exfat_hash_inode`, `exfat_unhash_inode`, `exfat_iget`
- `exfat_evict_inode`, `exfat_block_truncate_page`

## Key Data Flow
`__exfat_write_inode()` writes VFS inode state back into the file and stream directory entries: attributes, create/modify/access times, size, valid size, allocation flags, start cluster, and checksum. Root and deleted entries are skipped.

`exfat_map_cluster()` maps a file cluster offset to a disk cluster, allocating clusters when requested. It handles no-FAT arithmetic mapping, FAT-chain cached mapping, new allocation, FAT-chain conversion, and hint updates. `exfat_get_block()` turns this into block mappings for buffered I/O, direct I/O, bmap, readahead, and writeback, carefully treating unwritten space beyond valid size.

The file also defines address-space operations using mpage/block helpers, direct I/O, and truncate locking. Inode hashing maps exFAT directory position (`i_pos`) to in-memory inode reuse.

## Dependencies
Uses directory entry-set helpers, allocation/FAT/cache code, misc timestamp/checksum helpers, VFS inode/page-cache APIs, and `s_lock`/`truncate_lock`.

## Notable Invariants And Risks
- `valid_size` controls zero-fill behavior for unwritten allocated blocks.
- Truncation must serialize with bmap/direct mapping through `truncate_lock`.
- Inode identity is based on directory-entry position, not a native on-disk inode number.
- Evicting unlinked inodes truncates/free clusters under `s_lock`.
