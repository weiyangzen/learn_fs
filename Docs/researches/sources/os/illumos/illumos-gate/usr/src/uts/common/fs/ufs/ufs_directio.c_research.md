# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_directio.c

## Purpose

`ufs_directio.c` implements UFS direct I/O for aligned file reads and writes that bypass the page cache and issue physical buffer I/O directly to the backing device or snapshot strategy layer. It also initializes direct-I/O kstats and a kmem cache for reusable `buf_t` wrappers.

The file is performance-oriented but correctness-sensitive because it must coordinate page cache invalidation, mmap exclusion, block allocation, partial failures, POSIX synchronous data-integrity constraints, snapshots, and user-page locking.

## Main Interfaces

Public entry points include:

- `directio_bufs_init()` creates `directio_buf_cache`.
- `ufs_directio_init()` installs the `ufs/directio` kstat and allocates the private zero buffer used for hole reads.
- `ufs_directio_write()` attempts direct writes, returning `DIRECTIO_SUCCESS` or `DIRECTIO_FAILURE` through `statusp`.
- `ufs_directio_read()` attempts direct reads, also reporting success/failure through `statusp`.

Private helpers include `directio_buf_constructor()`, `directio_buf_destructor()`, `directio_wait_one()`, `directio_wait()`, `directio_start()`, and `directio_hole()`.

## Direct I/O Buffers And Accounting

Each physical I/O request uses a `struct directio_buf` containing a `buf_t`, target address, byte count, and reverse-order list link. The buffer is initialized once by `bioinit()` in the slab constructor and finalized with `biofini()` in the destructor.

`directio_start()` fills device, logical block, byte count, user address, process, vnode, flags, and optional page shadow list. It issues the I/O through `fssnap_strategy()` when snapshots are present, otherwise `bdev_strategy()`. It updates logical/physical read/write kstats and per-LWP block counters.

`directio_wait_one()` waits with `biowait()`, computes an approximate completed-byte count for residual reporting, clears transient `buf_t` flags, and frees the wrapper. `directio_wait()` drains the reverse-order request list, preserving the first error.

## Write Path

`ufs_directio_write()` first declines direct I/O when the feature is disabled, the file is mmaped, the request exceeds `uio_llimit`, offset/resid are not sector aligned, the target is not a regular file, or the inode is the quota inode.

For synchronous allocating writes, it avoids direct I/O if the write would extend the file or if the file has holes, because synchronous allocation under direct mode is slow and historically risky. For misaligned iovec lengths or bases, it may allocate a temporary aligned kernel buffer and copy user data into it before continuing.

For non-rewrite writes, the function allocates blocks with `bmap_write()` before issuing physical I/O. It extends `i_size` as blocks are allocated, sets large-file superblock state when crossing `MAXOFF32_T`, and rolls back with `ufs_itrunc()` if allocation fails after partial growth.

Before direct writes it invalidates cached pages with `VOP_PUTPAGE(..., B_INVAL, ...)`, upgrading `i_contents` to writer when needed. Shared-lock rewrites are tracked by `ufs_shared_writes`, `ufs_cur_writes`, and `ufs_maxcur_writes`; if cached pages appear during shared direct writes, they are invalidated afterward to avoid stale cache data.

Actual I/O loops over iovecs and `vfs_ioclustsz` chunks, locks user pages with `as_pagelock(..., S_READ)`, maps file offsets to contiguous disk extents with `bmap_read()`, issues one or more `directio_start()` calls, waits for completion, unlocks pages, updates `uio` state, and adjusts residuals based on bytes completed.

If `FDSYNC` or `ufs_force_posix_sdi` applies to a rewrite, the code verifies that the write can be a single contiguous request; otherwise it upgrades to exclusive `i_contents` locking so concurrent readers cannot observe non-atomic data-integrity behavior.

## Read Path

`ufs_directio_read()` similarly declines direct I/O when disabled, mmaped, unaligned, or iovec bases/lengths are unsuitable. It treats reads starting at or beyond EOF as direct-I/O success with no residual change so the cached read path does not repeat EOF logic. Reads that would cross EOF are shortened, but only if the shortened length remains sector aligned.

The read path invalidates cached pages, locks destination pages with `as_pagelock(..., S_WRITE)`, maps extents with `bmap_read()`, and issues physical reads. Holes are handled by `directio_hole()`, which moves zeros from the private zero buffer into the caller's `uio` rather than issuing disk I/O.

On completion, `uio_resid` is reduced by completed bytes. The implementation reports partial failures by tracking bytes read or written independently from driver `b_resid`, because the comments do not assume all disk drivers maintain `b_resid` reliably.

## Invariants And Dependencies

Key invariants:

- Direct I/O is only attempted for sector-aligned offsets and lengths.
- Mapped files are excluded via `i_mapcnt`.
- Page cache data must be invalidated before bypass I/O proceeds.
- Allocating writes must allocate backing blocks before physical writes.
- Hole reads synthesize zeroes; direct writes must not target holes unless allocation has already handled them.
- Snapshot-aware filesystems route I/O through `fssnap_strategy()`.

This file depends on UFS block mapping (`bmap_read`, `bmap_write`, `bmap_has_holes`), truncation (`ufs_itrunc`), vnode page flushing (`VOP_PUTPAGE`), VM page locking (`as_pagelock`/`as_pageunlock`), buf strategy I/O, snapshots, UFS transaction macros for inode updates, and UFS mount fields such as `vfs_ioclustsz`.

## Research Notes

The main risks are stale page-cache interaction, residual accounting after partial physical I/O failure, direct write rollback after preallocation extends `i_size`, and the shared-lock rewrite path. The file is deliberately conservative: most unsuitable cases return success with `DIRECTIO_FAILURE` so callers can fall back to normal cached I/O.
