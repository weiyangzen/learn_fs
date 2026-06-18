# File Research: sources/os/linux/linux/fs/cachefiles/io.c

## Purpose
Implements CacheFiles netfs cache I/O operations using direct `kiocb` reads and writes against backing files, including read-source selection, sparse-file occupancy queries, write preparation, async completion, and netfs cache-ops registration.

## Main Elements
- I/O request wrapper: `struct cachefiles_kiocb` tracks the backing `kiocb`, object reference, completion callback, invalidation counter, skipped bytes, and pending write block accounting.
- Read path: `cachefiles_read()` optionally seeks to data, zero-fills holes, submits `vfs_iocb_iter_read()` with `IOCB_DIRECT`, and completes through `cachefiles_read_complete()`.
- Occupancy: `cachefiles_query_occupancy()` uses `SEEK_DATA` and `SEEK_HOLE`, rounded to cache granularity, to report cached extents.
- Write path: `__cachefiles_write()` submits direct writes, tracks `b_writing`, handles async completion in `cachefiles_write_complete()`, and sets `FSCACHE_COOKIE_HAVE_DATA`.
- Read preparation: `cachefiles_do_prepare_read()` chooses between cache read, server download, zero-fill, or invalid on-demand read by probing backing file holes and honoring cookie state.
- Write preparation: `__cachefiles_prepare_write()` enforces page/DIO alignment, checks free space, detects allocated extents, and punches partially allocated regions when space is insufficient.
- Netfs write integration: `cachefiles_prepare_write_subreq()` and `cachefiles_issue_write()` align write subrequests to `CACHEFILES_DIO_BLOCK_SIZE` before writing to cache.
- Operation lifetime: `cachefiles_begin_operation()` pins the object file in cache resources and `cachefiles_end_operation()` releases it.
- `cachefiles_netfs_cache_ops`: supplies CacheFiles read, write, issue-write, prepare-read, prepare-write, on-demand read preparation, occupancy, and cleanup callbacks.

## Dependencies And Integration
Connects CacheFiles objects to the netfs library through `netfs_cache_ops`. Uses VFS direct I/O iter operations, sparse-file seeks, fallocate hole punching, CacheFiles space accounting, on-demand request handling, FS-Cache cookie access waits, and tracepoints.

## Risk Notes
Alignment is strict because CacheFiles relies on DIO and avoids partial-cache-block writes. Read paths guard against invalidation races by comparing `inval_counter`. Seek errors and fallocate failures can mark the cache dead. Async `kiocb` lifetime depends on two references: submission and completion.
