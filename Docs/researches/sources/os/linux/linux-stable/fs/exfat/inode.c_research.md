# File Research: sources/os/linux/linux-stable/fs/exfat/inode.c

This file implements inode writeback, logical-to-physical block mapping, address-space operations, direct I/O handling, inode hash lookup by on-disk position, inode construction, and eviction.

Key elements:
- `__exfat_write_inode()` persists a non-root inode’s file and stream entries: attributes, create/modify/access times, logical size, valid size, allocation flags, start cluster, and directory checksum.
- `exfat_map_cluster()` maps or allocates clusters for a logical cluster offset, handling no-FAT contiguous chains, FAT chains, chain extension, and conversion to FAT-chain representation when appended allocation is not contiguous.
- `exfat_get_block()` maps filesystem blocks for buffered I/O, direct I/O, bmap, and writeback. It handles `valid_size` carefully so unwritten regions read as zero and partially valid blocks are read/zero-filled as needed.
- Address-space operations include mpage read/readahead/writepages, block write begin/end, direct I/O, bmap under `truncate_lock`, and buffer migration.
- `exfat_direct_IO()` updates `valid_size` for writes and zeroes unwritten tail data for reads crossing valid size.
- `exfat_hash_inode()`, `exfat_unhash_inode()`, and `exfat_iget()` maintain a per-superblock hash keyed by encoded directory location.
- `exfat_fill_inode()` initializes VFS inode fields from `struct exfat_dir_entry`, choosing directory vs file operations and setting timestamps, generation, nlink, mapping ops, size, and blocks.
- `exfat_build_inode()` reuses existing hashed inodes or creates and hashes a new inode.
- `exfat_evict_inode()` truncates data for unlinked inodes, clears pages, invalidates cluster cache, and unhashes the inode.

Important dependencies:
- Block mapping calls cluster cache (`cache.c`), FAT/bitmap allocation (`fatent.c`/`balloc.c`), and directory writeback (`dir.c`).
- File operations in `file.c` depend on `exfat_block_truncate_page()` and writeback behavior here.

Failure/edge behavior:
- Detects broken FAT chains when logical size exceeds allocated clusters.
- Maintains separate `i_size`, `i_blocks`, and `ei->valid_size`, which is central to exFAT correctness.
- Root inode is not written through normal directory-entry writeback.
