# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_file.c

## Purpose

Implements XFS regular file and directory file operations. This is the primary VFS-facing file operation layer for reads, writes, fsync, mmap faults, fallocate, remap/reflink, open/release, llseek, fadvise, and directory iteration.

## Main Responsibilities

- Provides file operation tables:
  - `xfs_file_operations`
  - `xfs_dir_file_operations`
- Handles fsync:
  - data writeback
  - log sequence forcing
  - realtime/log/data device cache flush ordering
  - directory fsync through log force
- Handles reads:
  - buffered reads
  - direct I/O reads
  - DAX reads
  - splice reads
- Handles writes:
  - common write checks
  - layout break handling
  - privilege/time updates
  - EOF zeroing
  - direct I/O aligned and unaligned paths
  - DAX writes
  - buffered writes
  - zoned buffered and direct writes
  - atomic direct writes via hardware atomic write or CoW fallback
- Handles direct I/O completion:
  - CoW completion
  - unwritten extent conversion
  - in-core and on-disk size updates
  - zoned write completion
- Handles fallocate:
  - punch hole
  - collapse range
  - insert range
  - zero range
  - unshare range
  - allocate range
  - zoned reservations for operations requiring out-of-place edge zeroing
- Handles reflink/dedupe remap through `xfs_file_remap_range`.
- Handles open/release heuristics:
  - NOWAIT and O_DIRECT capability
  - atomic write capability
  - directory readahead
  - post-EOF preallocation trimming on close
- Handles mmap:
  - DAX read/write faults
  - page_mkwrite and pfn_mkwrite
  - zoned write fault reservation
  - mmap prepare validation and vm_ops setup.
- Handles `SEEK_HOLE` and `SEEK_DATA` with iomap.

## Important Invariants

- Direct I/O must be sector aligned; unaligned filesystem-block DIO has stricter serialization.
- Unaligned direct I/O to reflink/CoW inodes falls back to buffered write only for CoW cases.
- EOF zeroing can require upgrading from shared to exclusive IOLOCK and restarting checks.
- AIO direct-write completion is responsible for extending EOF safely.
- DAX writes and faults require exclusive or shared mmap locking depending on remap state.
- Fallocate collapse/insert ranges must align to the inode allocation unit.
- Always-COW inodes cannot use ordinary preallocation.
- Zoned files require pre-reserved space before write/fallocate/fault paths allocate out of place.
- Reflink remap requires reflink feature support and handles partial-shortening semantics carefully.

## Dependencies

- Uses iomap for buffered, direct, DAX, writeback, seek, and fault operations.
- Uses XFS bmap/iomap/reflink helpers for mapping, CoW, unwritten conversion, file-space movement, and remap.
- Uses zoned allocation helpers for zoned realtime/data handling.
- Uses VFS write, mmap, fsync, splice, fadvise, lease, and page fault infrastructure.
- Uses XFS tracepoints and stats throughout.

## Research Notes

This is the central file I/O integration point. The high-risk logic is around lock mode transitions, direct I/O completion, EOF updates, partial block zeroing, reflink/CoW fallback, zoned reservations, and sync ordering across data/log/realtime devices.
