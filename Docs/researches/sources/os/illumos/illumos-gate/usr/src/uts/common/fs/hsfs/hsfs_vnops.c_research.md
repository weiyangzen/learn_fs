# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_vnops.c

## Role

Implements vnode operations for illumos HSFS, the High Sierra / ISO-9660 read-only filesystem. The file covers ordinary vnode entry points, directory reading, symlink handling, memory mapping/page-cache integration, and a custom read scheduler for slow optical media.

## Major Responsibilities

- Exposes the `hsfs_vnodeops_template` vnode operation table.
- Implements read-only file access through `hsfs_read`, `hsfs_getpage`, `hsfs_getapage`, and `hsfs_putpage`.
- Implements metadata and namespace VOPs: getattr, lookup, readdir, readlink, fid, access, seek, fsync, close, inactive.
- Supports mmap of regular files while rejecting shared writable mappings.
- Maintains hsnode lifecycle, vnode inactive cleanup, and page-cache invalidation behavior.
- Contains HSFS-specific physical I/O scheduling and readahead for CD/DVD-style media.

## Key Functions

- `hsfs_read()`: Performs regular and directory file reads through `segmap_getmapflt()`, carefully clipping reads to EOF and `MAXBSIZE`-aligned windows.
- `hsfs_getattr()`: Converts `hs_dirent` metadata into `vattr`, including timestamps, device numbers for special nodes, block counts, and sequence number.
- `hsfs_lookup()`: Handles empty name and `"."`, then delegates actual directory search to `hs_dirlook()`.
- `hsfs_readdir()`: Reads raw HSFS directory blocks, validates directory entry lengths, parses entries with `hs_parsedir()`, translates names and inode choices into `dirent64`, and handles Rock Ridge symlink/inode cases.
- `hsfs_readlink()`: Returns the symlink target stored in the hsnode directory entry.
- `hsfs_inactive()`: Releases the vnode reference and either frees the hsnode immediately or moves it through HSFS free-node handling depending on cached pages.
- `hsfs_getpage()` and `hsfs_getapage()`: Provide VM/page-cache page-in support, reject writes, compute sequential readahead, handle ISO-9660 interleaving and extended attribute record offsets, and issue block reads.
- `hsfs_getpage_ra()` and `hsfs_ra_task()`: Implement semi-asynchronous readahead using the HSFS scheduler and taskq cleanup.
- `hsfs_putpage()` and `hsfs_putapage()`: Handle page invalidation/freeing for a read-only filesystem; dirty HSFS pages are treated as impossible and forced to error/invalidate.
- `hsfs_map()`, `hsfs_addmap()`, `hsfs_delmap()`: Support read-only mmap and track mapping counts for mandatory locking checks.
- `hsfs_frlock()`: Delegates to generic file locking but disallows mandatory locking if mapped.
- `hsched_init()`, `hsched_fini()`, `hsched_invoke_strategy()`, `hsched_enqueue_io()`: Implement the custom HSFS read scheduler.

## HSFS I/O Scheduler

The scheduler is designed around slow optical media. It stores queued read requests in two AVL trees:

- `read_tree`: ordered by logical block number for C-LOOK/elevator behavior.
- `deadline_tree`: ordered by request timestamp, then block, to avoid starvation.

`hsched_invoke_strategy()` picks either the next C-LOOK request or an expired-deadline request, coalesces adjacent I/O where worthwhile, and dispatches to `bdev_strategy()`. Coalesced reads use a synthetic buffer and copy completed bytes into the original page-backed buffers before signaling their semaphores.

Important scheduler state:

- `hio_cache` and `hio_info_cache` avoid frequent small allocation overhead.
- `hsfs_taskq_nthreads` controls per-mount readahead taskq thread limit.
- `hsched_coalesce_min` avoids coalescing very small adjacent chains.
- `dev_maxtransfer` is discovered via LDI/DKIOCINFO and limits coalesced transfer size.
- `max_ra_bytes` bounds sequential readahead.

## Data and State

- `struct hsnode`: per-file HSFS vnode private data, including parsed directory entry, page-map count, readahead state, and node identity.
- `struct hsfs`: per-mount state including volume geometry, device vnode, hash lock, scheduler queue, and read/readahead counters.
- `struct hio`: one queued low-level I/O request.
- `struct hio_info`: readahead batch state released by taskq.
- Global tunables include `seq_contig_requests`, `hsfs_taskq_nthreads`, `hsched_coalesce_min`, and `use_rrip_inodes`.

## Edge Cases and Semantics

- HSFS is read-only: write page faults return `EROFS`; shared writable mmap returns `ENOSYS`.
- Reads past EOF return short reads or zero.
- Directory reads skip invalid/trailing junk entries and can log bogus disk warnings.
- ISO-9660 interleaving is handled when mapping file offsets to physical device blocks.
- Extended attribute records (`xar_len`) are skipped before data.
- Files with zero size or symlink data may use `HS_DUMMY_INO` unless Rock Ridge inode data is trusted.
- `hsfs_putpage()` accepts invalidation/freeing requests even though the filesystem cannot write dirty data.
- `hsfs_pathconf()` reports name maximum, 33 file size bits, and 1/100 second timestamp resolution.

## Dependencies

Uses VM and segmap primitives (`pvn_read_kluster`, `page_lookup`, `segmap_getmapflt`), buffer I/O (`bdev_strategy`, `biowait`, `bioinit`), vnode/VFS helpers, AVL trees, taskqs, LDI device queries, DTrace probes, HSFS parser helpers (`hs_parsedir`, `hs_dirlook`, `hs_filldirent`), and Rock Ridge/SUSP metadata.
