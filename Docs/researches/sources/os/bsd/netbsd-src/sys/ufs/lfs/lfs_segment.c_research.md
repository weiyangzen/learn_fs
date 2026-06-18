# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_segment.c

## Purpose

`lfs_segment.c` is the core LFS segment writer. It flushes vnodes, builds partial segments, gathers dirty buffers and pages, updates block and inode metadata, writes segment summaries/inode blocks/data clusters, advances log segments, writes superblocks, and completes asynchronous clustered I/O.

## Main Responsibilities

- Updates Ifile modification time with `lfs_imtime()`.
- Flushes a single vnode synchronously with `lfs_vflush()`.
- Iterates eligible vnodes for regular, dirop, empty, or cleaner writes with `lfs_writevnodes()`.
- Performs whole-filesystem segment writes and checkpoints through `lfs_segwrite()`.
- Writes file data, indirect blocks, and inode records through `lfs_writefile()` and `lfs_writeinode()`.
- Updates inode-address mappings in the Ifile and segment-use byte accounting via `lfs_update_iaddr()`.
- Gathers dirty buffers into FINFO entries with `lfs_gatherblock()` and `lfs_gather()`.
- Assigns new physical addresses and rewrites direct/indirect metadata through `lfs_updatemeta()` and `lfs_update_single()`.
- Starts new partial segments and clean log segments with `lfs_initseg()` and `lfs_newseg()`.
- Writes clustered async disk I/O with `lfs_writeseg()`.
- Writes superblocks and handles superblock/cluster completion workqueue callbacks.
- Maintains FINFO entries with `lfs_acquire_finfo()` and `lfs_release_finfo()`.

## Segment Write Flow

`lfs_segwrite()` decides whether a checkpoint is needed from flags, active segment pressure, explicit checkpoint requests, and clean-segment thresholds. It takes the writer lock before the segment lock when checkpointing, writes regular vnodes, then optionally writes DIROP vnodes under the writer lock, flushes directory-operation state, finalizes filesystem-level segment-use deltas, clears `SEGUSE_ACTIVE` on old segments for checkpoints, repeatedly writes the Ifile until stable, writes pending partial segments, and unlocks.

`lfs_writefile()` creates an FINFO entry, marks DIROP summaries, gathers appropriate data buffers depending on mode, uses `VOP_PUTPAGES(... PGO_LOCKED)` for normal regular files, gathers indirect blocks when required, and releases the FINFO. Cleaner writes gather only fake cleaner buffers; roll-forward drops direct buffers because their contents are already on disk.

`lfs_writeseg()` finalizes segment-use bytes, checks FINFO validity, counts inode blocks, timestamps the segment, marks buffers busy to protect checksums, cleanses `UNWRITTEN` indirect pointers when needed, computes data and summary checksums, updates free/dmeta counters, clusters buffers into `MAXPHYS` writes, submits async I/O, updates stats, and initializes the next partial segment if needed.

## Metadata Updates

`lfs_updatemeta()` sorts gathered buffers by logical block number, records the final fragment length, assigns physical addresses at the current log offset, and calls `lfs_update_single()` for each filesystem block in each gathered buffer. `lfs_update_single()` resolves the old block pointer through `ulfs_bmaparray()`, updates direct, single-indirect, or deeper indirect pointers, adjusts dinode block counts and fragment sizes, subtracts old segment bytes, and marks the Ifile dirty when segment-use entries change.

`lfs_writeinode()` allocates inode blocks in the current segment, updates inode times, copies dinodes, handles Ifile self-write corner cases, marks DIROP completion state, preserves old link count/size when cleaner writes DIROP vnodes, removes `UNWRITTEN` addresses from on-disk dinodes, finalizes per-inode truncation deltas, updates inode summary counts, and records the inode's new address.

## Segment Allocation

`lfs_initseg()` starts a new partial segment, rolling to a new segment when `LFS_PARTIAL_FITS` fails. It skips embedded superblocks and segment-zero label padding, records cleaner partial segment addresses, allocates a summary buffer, initializes `SEGSUM`, FINFO pointers, free-byte counters, and roll-forward flags.

`lfs_newseg()` honors log-wrap stop controls, marks the selected next segment dirty/active, shifts cleanerinfo clean counts to dirty, records last/current segment addresses, scans for the next clean segment while optionally skipping invalidated segments, increments active segment counts, and updates stats.

`lfs_rewind()` can move the write offset to a lower-numbered clean segment before a requested segment, consuming remaining availability in the current segment.

## Async Completion

`lfs_cluster_work()` completes clustered writes on a workqueue. It propagates errors to child buffers, clears `B_GATHERED`, unlocks LFS buffers whose delayed-write state is gone, invalidates ordinary cleaner-created regular-file buffers, restores page-daemon buffer state when needed, calls `biodone()`, marks vnodes modified if dirty buffers remain after output completion, wakes vnode waiters, frees copied cluster memory, releases pools, and decrements filesystem/segment I/O counters.

`lfs_super_work()` frees async superblock buffers, clears `lfs_sbactive`, decrements `lfs_iocount`, and wakes waiters. `lfs_free_aiodone()` frees malloc-backed temporary buffers.

## Concurrency Notes

This file is organized around strict segment-lock ownership. It also coordinates with `lfs_writer`, `lfs_lock`, vnode interlocks, `bufcache_lock`, vnode iterators, workqueues, and `v_numoutput` waits. Special paths avoid reclaim deadlocks, skip vnodes in incompatible vnode states, protect checksum windows by marking buffers busy, and ensure synchronous segment writes wait for outstanding cluster I/O.
