# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_inode.c

## Purpose

`lfs_inode.c` implements core LFS inode maintenance: inode lookup inside inode blocks, timestamp/update flushing, file truncation and growth, block release, delayed segment-use accounting, indirect-block truncation, and buffer invalidation after truncation.

## Main Responsibilities

- Finds the newest matching dinode in an inode block with `lfs_ifind()`.
- Implements `lfs_update()` for inode time/state updates and synchronous vnode flushes.
- Implements `lfs_truncate()` for file extension, shrink, symlink clearing, page-cache size changes, block-pointer clearing, quota/accounting updates, and dirty-buffer invalidation.
- Frees blocks through `lfs_blkfree()` while batching segment byte decrements by segment.
- Stores postponed truncation deltas in per-inode/per-filesystem rb trees and commits them through `lfs_finalize_ino_seguse()` and `lfs_finalize_fs_seguse()`.
- Recursively truncates direct, single, double, and triple indirect blocks through `lfs_indirtrunc()`.
- Invalidates clean and dirty buffers past a truncation boundary with `lfs_vtruncbuf()` while returning delayed-write space to `lfs_avail`.

## Truncation Flow

`lfs_truncate()` handles device/FIFO/socket no-op truncation, short symbolic links, no-size-change metadata updates, file growth, and file shrink. Growth allocates the last byte, uses page-cache allocation for regular files, reserves log space for non-page-cache paths, updates vnode and dinode sizes, and writes the allocated buffer when needed.

Shrink reserves enough log space for metadata rewrites, zeroes partial tail data when required, sets the VM object size, invalidates buffers/pages beyond the new EOF, clears dead direct and indirect pointers, deregisters logical blocks, and accumulates released logical and real block counts. It updates `i_lfs_effnblks`, dinode block counts, `bfree`, quota usage, `i_lfs_hiblk`, and removes empty files from the paging queue.

## Segment Accounting

Because old blocks are not actually reclaimed until the new metadata reaches the log, block frees are staged as `struct segdelta` records. `lfs_blkfree()` groups contiguous frees from the same segment; `lfs_update_seguse()` inserts or updates rb-tree deltas; `lfs_finalize_seguse()` later subtracts bytes from `SEGUSE::su_nbytes` and writes segment-use entries. This keeps truncation accounting synchronized with eventual inode/ifile writes.

## Concurrency Notes

Most destructive paths assert the segment lock. `lfs_update()` explicitly avoids flushing `VU_DIROP` vnodes during directory operations, waits for in-progress writes on synchronous close/update, and coordinates with `lfs_writer`, `lfs_diropwait`, and `lfs_diropscv`. `lfs_vtruncbuf()` uses the vnode VM object lock and `bufcache_lock`, retries around `bbusy()` races, clears `BO_DELWRI`, unlocks LFS-locked buffers, and wakes `lfs_availsleep`.
