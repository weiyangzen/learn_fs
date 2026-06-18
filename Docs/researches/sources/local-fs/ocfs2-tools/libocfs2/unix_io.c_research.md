# File Research: sources/local-fs/ocfs2-tools/libocfs2/unix_io.c

Provides the Unix/Linux-backed `io_channel` implementation for libocfs2. It wraps file descriptor I/O, optional direct I/O, optional block caching, libaio vector reads, and I/O statistics.

Key responsibilities:
- Opens devices/files with `open64()`, normally using `O_DIRECT` unless buffered mode is requested.
- Reads/writes blocks via `pread64()` and `pwrite64()`.
- Provides libaio vector reads through `io_submit()` / `io_getevents()`.
- Maintains an optional cache using an rbtree for lookup and an LRU list for eviction.
- Supports shared caches across channels and optional `mlock()` pinning.
- Exposes stats for bytes read/written and cache hits/misses/inserts/removes.

Important functions:
- `io_open()` / `io_close()`: lifecycle for `io_channel`.
- `io_read_block()` / `io_write_block()`: normal block I/O with cache participation if enabled.
- `io_read_block_nocache()` / `io_write_block_nocache()`: avoid inserting new cache entries while updating existing ones.
- `io_vec_read_blocks()`: asynchronous vector read path.
- `io_init_cache()`, `io_init_cache_size()`, `io_destroy_cache()`, `io_share_cache()`.
- `io_validate_o_direct()`: probes viable block size for direct I/O.

Dependencies:
- POSIX/Linux I/O APIs, `libaio`, `linux/fs.h` for `BLKROGET`.
- `ocfs2/kernel-rbtree.h`, kernel-style list helpers, libocfs2 allocation wrappers.

Research notes:
- Negative `count` means byte count rather than block count in low-level read/write helpers.
- Cache correctness assumes cached blocks match disk contents; writes update cache after completed I/O.
- The direct-I/O validation loop tries block sizes from current size up to `OCFS2_MAX_BLOCKSIZE`.
- Includes a legacy Linux 2.4 block-device file-size-limit workaround.
