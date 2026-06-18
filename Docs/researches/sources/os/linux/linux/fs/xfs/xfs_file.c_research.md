# File Research: sources/os/linux/linux/fs/xfs/xfs_file.c

Implements XFS regular-file and directory file operations, including fsync, reads, writes, fallocate, reflink remap, mmap faults, open/release, readdir, and seek.

Key areas:
- Alignment and fsync:
  - `xfs_is_falloc_aligned` checks allocation-unit alignment, including non-power-of-two realtime units.
  - `xfs_dir_fsync`, `xfs_fsync_flush_log`, and `xfs_file_fsync` flush data, force relevant log sequence numbers, and issue device cache flushes for separate data/log/realtime devices.
- Reads:
  - `xfs_file_read_iter` dispatches to DAX, direct I/O, or buffered reads.
  - Direct reads use iomap and optional bounce buffering for stable writes.
  - `xfs_file_splice_read` wraps page-cache splice reads under IOLOCK.
- Write setup:
  - `xfs_ilock_iocb` and `xfs_ilock_iocb_for_write` implement nowait-aware IOLOCK acquisition and upgrade when reflink remap is active.
  - `xfs_file_write_zero_eof` and `xfs_file_write_checks` handle generic write checks, layout breaking, privilege removal requirements, zeroing gaps beyond EOF, and modified-time setup.
  - Zoned filesystems reserve space before writes through `xfs_zoned_write_space_reserve`.
- Direct/DAX/buffered writes:
  - `xfs_dio_write_end_io` and `xfs_zoned_dio_write_end_io` handle completion, COW/unwritten conversion, stats, and EOF updates.
  - `xfs_file_dio_write_aligned`, `_unaligned`, `_zoned`, and `_atomic` cover sector/block alignment, COW fallback, zone allocation, and hardware/COW atomic write paths.
  - `xfs_file_dax_write` uses DAX iomap and updates size synchronously.
  - `xfs_file_buffered_write` and `_zoned` use iomap buffered writes, retrying after quota/space cleanup or writeback.
  - `xfs_file_write_iter` validates atomic constraints and dispatches the correct write path, allowing direct I/O to fall back only for reflink CoW.
- Fallocate and remap:
  - Handles punch hole, collapse range, insert range, zero range, unshare range, and allocate range.
  - Zoned fallocate pre-reserves edge-zeroing space.
  - `xfs_file_remap_range` implements reflink/dedupe remap with prep, block remap, destination update, optional cowextsize hint propagation, and sync-log handling.
- Open/release/readdir/seek:
  - `xfs_file_open` sets nowait, direct I/O, and atomic write capability.
  - `xfs_dir_open` performs directory data readahead.
  - `xfs_file_release` triggers early writeout after truncation and opportunistic EOF-block cleanup.
  - `xfs_file_readdir` delegates to XFS directory iteration with a buffer-size estimate.
  - `xfs_file_llseek` supports `SEEK_HOLE` and `SEEK_DATA` through iomap.
- mmap faults:
  - DAX read/write faults use `dax_iomap_fault`.
  - Buffered write faults use `iomap_page_mkwrite`.
  - Zoned write faults reserve space for the folio.
  - `xfs_file_mmap_prepare` validates DAX synchronous mapping support and installs XFS vm ops.
- Operation tables:
  - `xfs_file_operations` wires regular-file methods and flags such as mmap sync, async buffered IO, parallel DIO writes, and dontcache.
  - `xfs_dir_file_operations` wires directory methods.

The file is the main VFS integration point for XFS data I/O and carefully coordinates IOLOCK/MMAPLOCK ordering, DAX vs page cache behavior, reflink/COW semantics, zoned allocation, direct I/O completion, and persistent metadata ordering.
