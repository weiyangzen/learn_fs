# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_pages.c

## Purpose

`lfs_pages.c` implements LFS vnode page operations. It wraps `genfs_getpages()`/`genfs_putpages()` with LFS log-write semantics, block-aligned dirty-page handling, pagedaemon deferral, segment-lock integration, and metadata/FINFO updates for gathered page buffers.

## Getpages

`lfs_getpages()` rejects writable mappings of the Ifile with `EPERM`. Writable access to other files marks the inode `IN_MODIFIED` under `lfs_lock`, then delegates to `genfs_getpages()`. The implementation relies on `genfs_getpages()` reading whole filesystem blocks.

## Dirty-Page Normalization

`check_dirty()` scans the page range by filesystem block and ensures block-level consistency: if any page in a block is dirty, all resident pages in that block are marked dirty. For `PGO_FREE`, pages are wired and flagged `PG_DELWRI` so the pagedaemon will not repeatedly process pages that are already queued for LFS writing. Busy pages cause bail-out when the pagedaemon or segment-locked caller could deadlock.

`wait_for_page()` and `write_and_wait()` handle busy pages, including flushing already gathered buffers with `lfs_writeseg()` so pages can complete their journey to disk.

## Putpages Flow

`lfs_putpages()` ignores metadata/Ifiles and non-regular vnodes, handles empty page objects by removing the inode from the LFS paging queue, and expands requested ranges to filesystem-block boundaries. Clean or non-cleaning requests are delegated to `genfs_putpages()`/`genfs_do_putpages()`.

For dirty pages, pagedaemon callers do not write directly. Instead, the inode is put on `lfs_pchainhd`, `IN_PAGING` is set, `lfs_writerd_cv` is broadcast, and `EWOULDBLOCK` is returned.

Non-pagedaemon dirty cleaning acquires or reuses the segment lock, creates an FINFO entry unless the caller already provided one via `PGO_LOCKED`, marks DIROP summaries when necessary, loops through `genfs_do_putpages()` until pages are gathered, gathers indirect blocks for non-locked callers, calls `lfs_updatemeta()`, releases FINFO, writes the segment, and removes the vnode from the paging queue when all pages were written.

## Directory Operation Handling

If a dirty vnode has `VU_DIROP` and the call is not already segment-locked, `lfs_putpages()` flushes pending directory operations through `lfs_flush_fs()` and retries. This avoids writing a newly created file's inode before the directory operation that makes it reachable has completed.

## Concurrency Notes

The function is built around the vnode VM object lock and intentionally drops/reacquires it around filesystem transactions and segment-lock acquisition. It uses `PGO_BUSYFAIL` to prevent deadlocks, translates `EDEADLK`/`EAGAIN` from genfs into retry or flush behavior, and strips `PGO_SYNCIO` before the actual LFS gather because `lfs_segunlock()`/explicit waits perform synchronization.
