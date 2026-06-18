# File Research: sources/os/linux/linux-stable/fs/cachefiles/io.c

This file implements CacheFiles data-path operations for netfs cache reads, writes, occupancy queries, read preparation, write preparation, and cache-resource operation setup.

I/O request wrapper:
- `struct cachefiles_kiocb` embeds a `kiocb`, refcount, range information, object pointer, termination callback, invalidation counter, async flag, and write block reservation count.
- `cachefiles_put_kiocb()` releases object and file references on final put.

Read path:
- `cachefiles_read()` waits for read access, optionally seeks for data with `SEEK_DATA`, zero-fills holes depending on requested hole behavior, allocates a direct-I/O kiocb, submits `vfs_iocb_iter_read()`, and reports completion through `cachefiles_read_complete()`.
- `cachefiles_read_complete()` validates the cookie invalidation counter before accepting successful data and converts stale completion to `-ESTALE`.
- `cachefiles_query_occupancy()` uses `SEEK_DATA` and `SEEK_HOLE` to report cached data ranges rounded to cache granularity.

Write path:
- `__cachefiles_write()` allocates a direct write kiocb, accounts pending blocks in `cache->b_writing`, submits `vfs_iocb_iter_write()`, and finalizes through `cachefiles_write_complete()`.
- `cachefiles_write_complete()` ends async write accounting, subtracts reserved pending blocks, marks the cookie as having data, invokes completion, and releases references.
- `cachefiles_write()` gates writes on FS-Cache operation state.

Read preparation:
- `cachefiles_do_prepare_read()` decides whether a netfs subrequest should read from cache, fill zeroes, download from server and copy to cache, or perform on-demand read.
- It handles EOF, no-data cookies, missing backing files, `SEEK_DATA/SEEK_HOLE` boundaries, and on-demand fetch/retry behavior.
- `cachefiles_prepare_read()` and `cachefiles_prepare_ondemand_read()` are wrappers for ordinary and on-demand paths.

Write preparation:
- `__cachefiles_prepare_write()` enforces page/DIO alignment, rounds length, checks cache space, detects allocated versus unallocated regions using `SEEK_DATA/SEEK_HOLE`, and punches holes when partially allocated regions cannot be safely overwritten under low-space conditions.
- `cachefiles_prepare_write()` performs file availability wait and credential override.
- `cachefiles_prepare_write_subreq()` sets netfs write stream limits and ensures the file exists.
- `cachefiles_issue_write()` trims or extends netfs write subrequests to `CACHEFILES_DIO_BLOCK_SIZE` boundaries, prepares space, and submits cache writes.

Operation setup:
- `cachefiles_begin_operation()` installs `cachefiles_netfs_cache_ops` into `netfs_cache_resources`, snapshots the object file under `object->lock`, and validates file presence unless only parameters are wanted.
- `cachefiles_end_operation()` drops the cached file reference and ends FS-Cache cookie access.

Important design details:
- Cache I/O is direct I/O (`IOCB_DIRECT`) and write uses `IOCB_WRITE`.
- `memalloc_nofs_save()` prevents filesystem recursion problems during backing I/O.
- Pending block accounting prevents `cachefiles_has_space()` from overestimating available cache space.
- On-demand mode reuses the same preparation logic but can trigger userspace fetches before retrying cache reads.
