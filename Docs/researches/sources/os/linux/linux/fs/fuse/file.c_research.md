# File Research: sources/os/linux/linux/fs/fuse/file.c

Purpose: Implements FUSE regular-file operations, including open/release, cached reads/writes, writeback, direct IO, mmap, locks, poll, bmap, lseek, fallocate, splice, and copy_file_range.

Key responsibilities:
- Handles `FUSE_OPEN`/`FUSE_RELEASE` lifecycle through `fuse_file_open()`, `fuse_finish_open()`, `fuse_prepare_release()`, and refcounted `struct fuse_file`.
- Supports no-open/no-opendir server optimizations while still allocating release state when needed to avoid reclaim deadlocks.
- Implements flush and fsync semantics, including writeback synchronization, metadata sync, and server fallback when `FUSE_FLUSH` or `FUSE_FSYNC` is unsupported.
- Provides cached read path using iomap folio reads and readahead, issuing `FUSE_READ` requests and handling short-read EOF truncation.
- Provides cached write path using either iomap buffered write for writeback-cache mode or immediate FUSE write requests through `fuse_perform_write()`.
- Implements writeback with `struct fuse_writepage_args`, queued writepage requests, sync buckets for `syncfs`, and `FUSE_WRITE_CACHE`.
- Implements direct IO through `fuse_direct_io()`, packing user pages or kernel vectors into request pages/args and supporting async DIO.
- Enforces direct-write locking rules, including exclusive locking for append, writes past EOF, non-parallel servers, or cache-mode conflicts.
- Implements mmap behavior for DAX, passthrough, direct-IO shared mmap restrictions, cached mmap, and `page_mkwrite` writeback ordering.
- Implements POSIX locks, BSD flock mapping, `FUSE_BMAP`, `FUSE_LSEEK`, `FUSE_POLL`, `FUSE_FALLOCATE`, and `FUSE_COPY_FILE_RANGE(_64)`.
- Exposes `fuse_file_operations`, `fuse_file_aops`, and `fuse_init_file_inode()`.

Important data/control flow:
- `ff->open_flags` decides direct IO, keep-cache, stream/nonseekable, passthrough precedence, mmap behavior, and direct write concurrency.
- `fi->write_files` tracks open writable files needed for writeback and metadata flushes.
- `fi->queued_writes`, `fi->writectr`, and `FUSE_NOWRITE` coordinate truncate/fsync/writeback exclusion.
- Async direct IO uses `struct fuse_io_priv` refcounts, completion accounting, byte aggregation, and `ki_complete()`.
- `fuse_write_update_attr()` bumps attribute version, extends local size when needed, and invalidates modsize stats.

External dependencies:
- FUSE connection and request structures from `fuse_i.h`.
- DAX helpers, passthrough helpers, iomap buffered IO/writeback APIs, folio APIs, VFS locking and splice APIs.
- Server request transport via `fuse_simple_request()` and `fuse_simple_background()`.

Notable edge cases:
- `FOPEN_DIRECT_IO` overrides passthrough.
- Writeback-cache trusts local size/mtime/ctime more than server attributes.
- Async DIO cannot extend file size without blocking behavior.
- Copy file range falls back from 64-bit opcode to old opcode, then to splice fallback for unsupported/cross-device cases.
- Fallocate hole punch/zero range writes back and invalidates page cache to prevent stale data.
