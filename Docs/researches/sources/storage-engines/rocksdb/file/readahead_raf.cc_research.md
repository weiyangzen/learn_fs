# sources/storage-engines/rocksdb/file/readahead_raf.cc

## Purpose

`readahead_raf.cc` implements `NewReadaheadRandomAccessFile`, a wrapper that adds fixed-size read-ahead caching on top of an `FSRandomAccessFile`. It is mainly used by compaction table readers to fetch extra data with reads and reduce repeated filesystem calls during sequential-ish access.

## Important APIs, Types, and Functions

- Internal `ReadaheadRandomAccessFile` derives from `FSRandomAccessFile`.
- Constructor stores the wrapped file, required alignment, rounded readahead size, aligned buffer, and initial buffer offset.
- `Read(...)` serves data from the cache when possible, otherwise reads an aligned readahead chunk into the internal buffer and copies requested bytes to caller scratch.
- `Prefetch(...)` fills the internal buffer, but ignores requests smaller than configured readahead size.
- Forwarders: `GetUniqueId`, `Hint`, `InvalidateCache`, `use_direct_io`, and `GetFileSize`.
- Private `TryReadFromCache(...)` copies cached bytes.
- Private `ReadIntoBuffer(...)` reads aligned data into `buffer_` and updates `buffer_offset_`/size.
- `NewReadaheadRandomAccessFile(...)` constructs the wrapper.

## Control Flow and State

The constructor rounds `readahead_size` up to filesystem alignment, sets buffer alignment, and allocates the buffer. `Read` bypasses readahead when the caller's request is too large to leave useful slack. Otherwise it locks, tries to copy a complete or partial cache hit, and returns immediately if the full request is satisfied or the short buffer indicates EOF. On miss/partial hit it advances to the first uncached byte, truncates to an aligned chunk offset, reads up to the configured readahead size into the cache, then copies the remaining requested bytes from cache.

`Prefetch` refuses smaller-than-configured prefetches because `Read` treats a buffer shorter than `readahead_size_` as EOF. For valid requests it aligns the offset, skips if already at the same buffer offset, and reads the requested aligned range capped by buffer capacity.

The wrapper maintains mutable in-memory cache state protected by a mutex: `buffer_` and `buffer_offset_`. It does not persist anything.

## Dependencies and Integration Points

It depends on `read_write_util.h` for debug alignment assertions, `FSRandomAccessFile`, `AlignedBuffer`, and rate-limiter utilities for rounding helpers. It integrates as a drop-in `FSRandomAccessFile` wrapper, preserving unique id, hints, direct-IO mode, and file size behavior from the target.

## Risks and Edge Cases

- `Read` copies into caller scratch, so scratch must be large enough even when cache hits span partial buffers.
- Requests with `n + alignment >= readahead_size_` bypass the cache, so small readahead sizes can disable benefits.
- `Prefetch` no-ops for small requests by design; callers expecting exact prefetch length may be surprised.
- The implementation assumes aligned offset/length for buffer reads and asserts in debug.
- `offset + n` arithmetic is converted through `size_t`; extremely large offsets could be risky on 32-bit platforms.

## Test Signals

Direct tests are not in this subset, but `prefetch_test.cc` covers broader prefetch behavior and `read_write_util` alignment assertions protect this implementation in debug builds. Compaction table-reader tests should observe reduced read calls when this wrapper is active.
