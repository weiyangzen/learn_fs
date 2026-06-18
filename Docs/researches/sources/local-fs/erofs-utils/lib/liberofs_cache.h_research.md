# File Research: sources/local-fs/erofs-utils/lib/liberofs_cache.h

This header defines the buffer manager API used to allocate, attach, map, flush, and drop metadata/data buffers while constructing an EROFS image.

Core types:
- Buffer types: `DATA`, `META`, `INODE`, `DIRA`, `XATTR`, `DEVT`.
- `struct erofs_bhops`: flush callback interface for buffer heads.
- `struct erofs_buffer_head`: linked buffer item with offset, ops, and private data.
- `struct erofs_buffer_block`: physical/logical block bucket containing buffer heads.
- `struct erofs_bufmgr`: global manager with watermeter buckets, block header, target vfile, device-alignment settings, and mapping cache.

Important inline:
- `get_alignsize()` maps logical allocation types to alignment and storage type. Inode, directory, xattr, and device table allocations are redirected to metadata alignment rules.
- `erofs_btell()` computes the byte position of a buffer head from block address and intra-block offset.
- `erofs_bh_flush_generic_end()` removes and frees a buffer head.

External API:
- `erofs_buffer_init()`, `erofs_buffer_exit()`
- `erofs_balloc()`, `erofs_battach()`, `erofs_bdrop()`
- `erofs_bh_balloon()`
- `erofs_mapbh()`, `erofs_bflush()`

Known users:
- Inode placement and inline data.
- Directory and file data block reservation.
- Metadata zone and metabox staging.
- Device table writing.

Risks / notes:
- Many higher-level components assume `erofs_mapbh()` finalizes addresses before NID/blockaddr derivation.
- `watermeter` is sized by `EROFS_MAX_BLOCK_SIZE`, so block-size assumptions are baked into allocation bucketing.
