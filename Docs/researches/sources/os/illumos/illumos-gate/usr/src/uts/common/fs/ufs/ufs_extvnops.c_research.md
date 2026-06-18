# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_extvnops.c

## Purpose

`ufs_extvnops.c` provides UFS support for external vnode-style data operations using `fdbuffer_t`. It is designed for reads/writes where data movement can be done through filesystem block mappings and device strategy I/O rather than ordinary user `uio` paths.

The file exposes two operations: one for read/write when file size and allocation must not change, and one for allocation plus optional I/O when file size or sparse regions may need to change.

## Main Interfaces

- `ufs_rdwr_data()` reads or writes existing allocated file data into an `fdbuffer_t`. It refuses to allocate blocks or grow the file.
- `ufs_alloc_data()` allocates backing store and optionally performs I/O through an `fdbuffer_t`; it can grow the file and fill holes.

Both functions obey lockfs through `ufs_lockfs_begin_getpage()`, use `i_contents` locking, coordinate with quota locking through `vfs_dqrwlock`, use `bmap_read()`/`bmap_write()`, and route physical I/O through snapshots when present.

## `ufs_rdwr_data()`

`ufs_rdwr_data()` begins the getpage-oriented lockfs protocol, caps I/O length to `i_size`, and takes `vfs_dqrwlock` plus `i_contents` as reader. It then loops over the requested range, translating file offsets to disk blocks with `bmap_read()`.

For allocated extents, it builds fdbuffer I/O buffers with `fdb_iosetup()`, fills device/block/vnode/offset fields, and submits them through `fssnap_strategy()` or `bdev_strategy()`. Synchronous requests wait with `biowait()` and finish each buffer with `fdb_iodone()`.

For holes, reads add a hole record to the fdbuffer with `fdb_add_hole()`. Writes are not expected to encounter holes; the code asserts that and returns `ENOSPC` if a write hole is seen.

Asynchronous operation calls `fdb_ioerrdone()` when no more I/O will be added. If at least one async I/O was started, the function returns zero and lets completion carry errors through the fdbuffer path.

## `ufs_alloc_data()`

`ufs_alloc_data()` is the heavier path because it can allocate space and grow the file inside a UFS log transaction. It begins lockfs, attempts `TRANS_TRY_BEGIN_CSYNC()` for `TOP_GETPAGE`, and returns `EDEADLK` for async fdbuffer callers if the transaction cannot begin without blocking.

With `i_contents` as writer, it walks filesystem blocks covering the requested range. If a block extends beyond EOF, it calls `bmap_write(..., BI_ALLOC_ONLY, ...)`, optionally records holes for bytes beyond old EOF, performs I/O for the pre-existing tail if needed, updates `i_size`, logs the inode, and sets `FSLARGEFILES` when the file crosses the legacy 2 GB threshold.

If the range is inside EOF, allocated blocks can be read/written through fdbuffer I/O. Holes are allocated with `bmap_write()` and reported as holes to the fdbuffer so callers know those bytes were logically absent before allocation.

On allocation failure after file growth, the function truncates back to `old_i_size`. Before returning it rounds `*len` to a fragment or block boundary, invalidates cached pages with `VOP_PUTPAGE(..., B_INVAL, ...)`, closes the transaction, and ends lockfs.

## Invariants And Dependencies

Key invariants:

- `ufs_rdwr_data()` must not allocate blocks or change file length.
- `ufs_alloc_data()` must be used when allocation or growth may occur.
- Writes through these paths bypass the page cache but still invalidate pages before completion.
- Async fdbuffer callers need `fdb_ioerrdone()` even on early lockfs/transaction failures.
- File-size growth is logged and rolled back on error.

Dependencies include `fdbuffer` APIs, lockfs getpage protocol, UFS block mapping/allocation, UFS transactions, snapshot strategy I/O, inode timestamps/sequence updates, large-file superblock state, and page invalidation.

## Research Notes

This file is a specialized bridge between UFS block allocation and fdbuffer consumers. It is smaller than the ordinary vnode I/O path but sensitive to transaction begin semantics, async error signaling, and cache invalidation after bypass I/O.
