# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_blockdev.c

Block device abstraction and cache integration layer. It wraps physical device callbacks, maps ext4 logical block IO to physical block IO, handles cached block get/release, byte-range IO, cache flushing, and writeback mode.

Key behavior:
- `ext4_block_init` opens the underlying block interface once and maintains a physical reference count.
- `ext4_block_set_lb_size` sets ext4 logical block size and computes logical block count from partition size.
- `ext4_block_get_noread` and `ext4_block_get` allocate cache buffers, optionally read backing storage, and mark buffers up-to-date.
- `ext4_block_set` releases a cached block back through `ext4_bcache_free`.
- `ext4_blocks_get_direct` and `ext4_blocks_set_direct` convert logical block addresses to physical block addresses using `part_offset`, logical block size, and physical block size.
- `ext4_block_writebytes` and `ext4_block_readbytes` implement unaligned byte IO with read-modify-write/read of edge physical blocks.
- `ext4_block_cache_shake`, `ext4_block_cache_flush`, and `ext4_block_cache_write_back` evict/flush LRU and dirty buffers.

Notable dependencies:
- `ext4_bcache` owns buffer objects and dirty/LRU structures.
- Physical IO is delegated to `struct ext4_blockdev_iface` callbacks (`open`, `close`, `bread`, `bwrite`, optional `lock`/`unlock`).

Research notes:
- Lock/unlock wrapper assertions assume the block interface lock callbacks cannot fail.
- Byte-range IO validates against `part_size`, but direct logical block IO relies on logical count checks at cached get time.
- `ext4_block_flush_buf` invokes optional completion callbacks with `dont_shake` set to avoid recursive cache eviction.
