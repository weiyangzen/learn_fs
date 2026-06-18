# File Research: sources/os/linux/linux/fs/zonefs/file.c

## Purpose

Implements zonefs regular file operations and address-space operations. Each file maps directly to a zone or aggregated conventional zones.

## Main Responsibilities

- Provides iomap mappings for reads, writes, writeback, and direct I/O.
- Supports buffered I/O only for conventional zone files.
- Enforces direct-only sequential-zone writes.
- Enforces append/write-pointer ordering for sequential zones.
- Handles truncate-to-zero as zone reset and truncate-to-capacity as zone finish.
- Updates inode size and zone write pointer on direct write completion.
- Handles fsync via page-cache writeback for conventional files and block flush.
- Supports mmap with shared writable mappings only for conventional files.
- Handles read, splice read, write, llseek, open, release, and swap activation.
- Implements explicit zone open/close accounting for sequential write opens.

## Important Invariants

- Sequential zone files accept writes only at `z_wpoffset`.
- Sequential direct writes must be block aligned.
- Sequential files cannot use buffered writes or shared writable mmap.
- Truncate is allowed only to 0 or zone capacity and only for sequential files.
- Async NOWAIT direct writes to sequential files are rejected to avoid reordering.
- Successful sequential write completion can advance inode size because preceding writes must also have completed.
- Explicit-open files must close zones on last writer close, but close errors are not returned from `close(2)`.

## Dependencies

Uses iomap buffered/direct/writeback APIs, block device flush and zone management via super.c helpers, inode locks, invalidate locks, mmap VM ops, and zonefs tracepoints.

## Research Notes

This is the central zonefs I/O enforcement layer. The key correctness property is keeping VFS inode size, `z_wpoffset`, and device write pointer consistent across writes, truncates, and error recovery.
