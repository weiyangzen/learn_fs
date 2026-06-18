# File Research: sources/os/linux/linux/fs/gfs2/bmap.c

Implements GFS2 block mapping, iomap integration, allocation, stuffed-file unstuffing, truncation, hole punching, journal extent mapping, and writeback extent lookup.

Major concepts:
- `struct metapath` represents a path through dinode and indirect metadata blocks.
- Stuffed inodes store data inline in the dinode; large writes/grows unstuff them into normal blocks.
- GFS2 maps data through a height-based indirect tree and uses iomap for buffered/direct I/O.

Key entry points:
- `gfs2_unstuff_dinode()`
- `gfs2_iomap_get()` / `gfs2_iomap_alloc()`
- `gfs2_block_map()`
- `gfs2_get_extent()` / `gfs2_alloc_extent()`
- `gfs2_setattr_size()`
- `gfs2_truncatei_resume()` / `gfs2_file_dealloc()`
- `gfs2_map_journal_extents()` / `gfs2_free_journal_extents()`
- `gfs2_write_alloc_required()`
- `__gfs2_punch_hole()`
- `gfs2_iomap_ops`, `gfs2_iomap_write_ops`, `gfs2_writeback_ops`

Important control flow:
- Mapping starts with `__gfs2_iomap_get()`, which handles inline data, holes, mapped extents, metadata height growth needs, and `IOMAP_REPORT`.
- Allocation uses `gfs2_iomap_begin_write()` to reserve quota/resource groups, start a transaction, unstuff if needed, and call `__gfs2_iomap_alloc()`.
- `__gfs2_iomap_alloc()` is a state machine for growing tree height, growing depth, and allocating contiguous data blocks.
- `gfs2_iomap_end()` releases reservations/quota, adjusts grow statfs for rindex writes, marks ordered inodes, and punches unwritten tail blocks if short writes left new allocations unused.
- Truncation uses `trunc_start()`, `punch_hole()`, and `trunc_end()` with `GFS2_DIF_TRUNC_IN_PROG` for crash recovery.
- `punch_hole()` walks metadata bottom-up/right-to-left, frees blocks per resource group, rewrites the dinode at transaction boundaries, and updates statfs/quota.
- Journal mapping caches logical-to-physical journal extents for efficient log I/O.

Dependencies and integration:
- Heavy integration with GFS2 glocks, metadata I/O, resource groups, quota, transactions, log, iomap, buffer heads, tracepoints, and directory unstuff support.
- `gfs2_block_map()` bridges legacy buffer-head users to iomap.

Risks and invariants:
- `gfs2_block_zero_range()` must not be called with an open transaction because iomap write paths begin their own transactions.
- Deallocation splits work by resource group and transaction thresholds to preserve consistency and concurrency.
- Short writes to newly allocated extents are cleaned up by pagecache truncation plus hole punch.
- Many corruption checks withdraw/mark consistency errors if metadata shape, block pointers, or metatypes are invalid.
